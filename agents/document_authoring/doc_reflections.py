from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_reflections(state: MainState) -> MainState:
    """
    doc_reflections is an AI agent that can be used to generate user reflections based on history.The main purpose is to help generate information/insights about the user and their needs.
    """
    logger.info("doc_reflections started with state: %s", json.dumps(state, indent=2))

    user_id = state['user_id']
    session_id = state['session_id']
    conversation_id = state['conversation_id']
    user_input = state['user_input']
    conversation_history = state['conversation_history']
    node_history = state['node_history']
    document_history = state['document_history']
    strategy_history = state['strategy_history']
    reflection_history = state['reflection_history']
    requirements_history = state['requirements_history']
    structure_history = state['structure_history']

    prompt = f"""
    You are an expert user behavior analyst. Your task is to analyze ALL of the user's historical interactions to create a comprehensive profile of their working style, preferences, and characteristics. Focus on identifying patterns across ALL their document requests, not just the current one.

    Context from previous interactions:
    {user_input}
    {conversation_history}
    {node_history}
    {document_history}
    {strategy_history}
    {reflection_history}
    {requirements_history}
    {structure_history}

    Please analyze the user's overall behavior and provide insights in this format:

    # User Behavioral Profile Analysis

    ## Message to Agent
    [IMPORTANT: Use this section to:
    - Highlight key patterns identified
    - Note any gaps in behavioral data
    - Request clarification on user context
    - Suggest areas for deeper analysis
    - Flag any inconsistent behaviors]

    ## User Profile Analysis
    [Comprehensive analysis of user behavior, including:
    - Working style and preferences
    - Communication patterns
    - Technical expertise
    - Decision-making approach
    - Quality expectations
    - Time management
    - Collaboration style
    - Learning patterns]

    Consider these aspects:
    1. Recurring themes in their requests
    2. Consistent communication patterns
    3. Long-term preferences and habits
    4. Evolution of their needs over time
    5. Common success factors
    6. Persistent challenges
    7. Adaptation patterns
    8. Professional context

    Your analysis should help:
    1. Build a comprehensive user profile
    2. Predict future needs
    3. Customize our approach
    4. Improve user satisfaction
    5. Reduce friction points
    6. Enhance efficiency
    7. Build better rapport
    8. Deliver consistent quality

    IMPORTANT: 
    - Focus on patterns across ALL interactions
    - Identify consistent behaviors
    - Note evolving preferences
    - Flag any contradictions
    - Suggest adaptation strategies

    Please provide your response in this JSON format:
    {{
        "message_to_agent": "Your analysis notes, missing information, clarifications needed, and recommendations for better understanding the user",
        "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
        "reflections": "MUST BE IN MARKDOWN FORMAT. The comprehensive user behavioral profile and analysis following the structure above"
    }}
    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert user behavior analyst."},
        {"role": "user", "content": prompt}
    ]

    #create a response id
    response_id = str(uuid.uuid4())

    try:
        llm_response = call_llm_api(messages)
        logger.info("LLM response: %s", llm_response)
        print("LLM response: %s", llm_response)
        # Parse the LLM response
        parsed_response = (llm_response)
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_reflections",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify user reflections in the reflection_history"
        })

        state["reflection_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_reflections",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_reflections agent with state: %s", json.dumps(state, indent=2))
    return state



