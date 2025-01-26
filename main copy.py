from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json

from shared_services.get_conversation_history import get_conversation_history
from shared_services.save_conversation import save_conversation
from shared_services.logger_setup import setup_logger

# Import agents and tools
from agents.document_authoring.document_authoring_agent import document_authoring_agent
from agents.document_authoring.template_generator_tool import template_generator_tool
from agents.document_authoring.instruction_to_document_tool import instruction_to_document_tool
from agents.document_authoring.content_enrichment_tool import content_enrichment_tool
from agents.document_authoring.chat_tool import chat_tool

logger = setup_logger()
app = FastAPI()

# In-memory session storage
active_sessions: Dict[str, Dict[str, Any]] = {}

class SessionStart(BaseModel):
    user_id: str
    session_id: str

class UserInput(BaseModel):
    user_id: str
    session_id: str
    input_text: str

@app.post("/start-session")
async def start_session(session_data: SessionStart):
    """Initialize a new session and load conversation history"""
    try:
        # Generate conversation_id
        conversation_id = (
            session_data.user_id + 
            session_data.session_id + 
            datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        )
        
        # Initialize state
        state = {
            "user_id": session_data.user_id,
            "session_id": session_data.session_id,
            "conversation_id": conversation_id,
            "user_input": "",  # Will be set when user provides input
            "kyc": {},
            "conversation_history": [],
            "node_history": [],
            "final_response": "",
            "document_history": [],
            "current_document": "",
        }
        
        # Load conversation history
        history = get_conversation_history(
            user_id=session_data.user_id,
            session_id=session_data.session_id,
            conversation_id=conversation_id,
            limit=10
        )
        
        if history["status"] == "success":
            state["conversation_history"] = history.get("conversation_history", [])
            state["node_history"] = history.get("node_history", [])
            logger.info("Loaded previous conversation history")
        
        # Store state in active sessions
        active_sessions[conversation_id] = state
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "message": "Session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user-input")
async def process_user_input(user_input: UserInput):
    """Process user input and return response"""
    try:
        # Find the active session
        conversation_id = (
            user_input.user_id + 
            user_input.session_id + 
            datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        )
        
        state = active_sessions.get(conversation_id)
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update state with user input
        state["user_input"] = user_input.input_text
        state["conversation_history"].append({
            "role": "user",
            "conversation_id": conversation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": user_input.input_text
        })
        
        # Process through agents and tools
        try:
            state = document_authoring_agent(state)
            state = template_generator_tool(state)
            state = document_authoring_agent(state)
            state = chat_tool(state)
            state = instruction_to_document_tool(state)
            state = document_authoring_agent(state)
            state = content_enrichment_tool(state)
            state = document_authoring_agent(state)
            state = chat_tool(state)
            
            # Update session state
            active_sessions[conversation_id] = state
            
            # Get latest message_to_human and document_content
            latest_node = state["node_history"][-1]
            tool_params = latest_node["content"]["selected_tools"][0]["parameters"]
            
            return {
                "status": "success",
                "message_to_human": tool_params.get("message_to_human", ""),
                "document_content": tool_params.get("document_content", "")
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Error in user input endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/end-session")
async def end_session(session_data: SessionStart):
    """End session and save state"""
    try:
        conversation_id = (
            session_data.user_id + 
            session_data.session_id + 
            datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        )
        
        state = active_sessions.get(conversation_id)
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save final state
        with open(f'output_{conversation_id}.json', 'w') as f:
            json.dump(state, f, indent=4)
        
        # Save conversation to DB
        save_conversation(state)
        
        # Clean up session
        del active_sessions[conversation_id]
        
        return {
            "status": "success",
            "message": "Session ended and saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))