from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json

from shared_services.get_conversation_history import get_conversation_history
from shared_services.save_conversation import save_conversation
from shared_services.logger_setup import setup_logger
from shared_services.shared_types import MainState

# Import agents and tools

from agents.document_authoring.chat_tool import chat_tool
from agents.document_authoring.doc_structure import doc_structure
from agents.document_authoring.doc_requirements import doc_requirements
from agents.document_authoring.doc_reflections import doc_reflections
from agents.document_authoring.doc_researcher import doc_researcher
from agents.document_authoring.doc_writer import doc_writer
from agents.document_authoring.doc_finisher import doc_finisher
from agents.document_authoring.doc_stratergy import doc_strategy

logger = setup_logger()

# initialize state
state = {
    "session_id": "123",
    "user_id": "4563",
    "conversation_id": "789",
    "document_id": "101",
    "user_input": "Hello, I need help with my document. I want a business case for a new product.",
    "conversation_history": [],
    "structure_history": [],
    "document_history": [],
    "strategy_history": [],
    "reflection_history": [],
    "requirements_history": [],
    "node_history": [],
    "research_history": []
}



def run_agents(state: MainState):
    """Run the document authoring agents"""
    # Get history directly
    history = get_conversation_history(
        state["user_id"],
        state["session_id"],
        state["conversation_id"],
        10
    )
    
    # Update the histories in current_state
    if history["status"] == "success":
        state["conversation_history"] = history["conversation_history"]
        state["node_history"] = history["node_history"]
        state["structure_history"] = history["structure_history"]
        state["requirements_history"] = history["requirements_history"] 
        state["reflection_history"] = history["reflection_history"]
        state["research_history"] = history["research_history"]
        state["strategy_history"] = history["strategy_history"]

    # Run document strategy agent
    state = doc_strategy(state)
    # Run document structure agent
    state = doc_structure(state)
    # Run document requirements agent
    state = doc_requirements(state)
    # Run document reflections agent
    state = doc_reflections(state)
    # Run document researcher agent
    state = doc_researcher(state)
   
    return state

if __name__ == "__main__":
    state = run_agents(state)
    print(state)
    # save the state to db
    save_conversation(state)
    # save the state to a file
    with open('state.json', 'w') as f:
        json.dump(state, f)


