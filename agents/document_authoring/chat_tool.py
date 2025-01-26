from typing import Dict, Any
from datetime import datetime, timezone
import json
from shared_services.shared_types import MainState
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def chat_tool(state: MainState) -> MainState:
    """
    Chat tool for handling user interactions. Shows messages to the user and collects their input.
    """
    try:
        # Get the latest node history entry
        latest_node = state.get("node_history", [])[-1]
        
        if latest_node["content"]["response_type"] != "chat-tool":
            logger.error("Chat tool called with incorrect response type")
            return state
            
        # Extract parameters from the tool call
        tool_params = latest_node["content"]["selected_tools"][0]["parameters"]
        message_to_human = tool_params.get("message_to_human", "")
        document_content = tool_params.get("document_content", "")
        
        # First, add assistant's message to conversation history
        state["conversation_history"].append({
            "role": "assistant",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": message_to_human
        })
        
        # Display message and document to user
        print("\n" + "="*80)
        print("MESSAGE FROM ASSISTANT:")
        print(message_to_human)
        
        if document_content:
            print("\nCURRENT DOCUMENT:")
            print(document_content)
        
        print("\nPlease provide your feedback or type 'done' if you're satisfied:")
        user_input = input("> ")
        
        # Immediately update conversation history with user's input
        state["conversation_history"].append({
            "role": "user",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": user_input
        })
        
        # Update user input in state for next iteration
        state["user_input"] = user_input
        
        # Update node history with the interaction result
        state["node_history"].append({
            "role": "AI_TOOL",
            "node": "chat_tool",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": {
                "response_type": "tool_response",
                "Responses": [{
                    "response_id": f"chat_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                    "reason": "User interaction completed",
                    "parameters": {
                        "user_input": user_input,
                        "interaction_status": "done" if user_input.lower() == "done" else "feedback_provided"
                    }
                }]
            }
        })
        
        logger.info("Chat interaction completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in chat tool: {e}")
        state["node_history"].append({
            "role": "AI_TOOL",
            "node": "chat_tool",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": {
                "response_type": "error",
                "error_message": str(e)
            }
        })
        return state 