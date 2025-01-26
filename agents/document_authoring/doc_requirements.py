from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_requirements(state: MainState) -> MainState:
    """
    doc_requirements is an AI agent that can be used to generate document requirements i.e what is needed to generate the document based on user requirements and context.
    """
    logger.info("doc_requirements started with state: %s", json.dumps(state, indent=2))

    user_id = state['user_id']
    session_id = state['session_id']
    conversation_id = state['conversation_id']
    document_id = state['document_id']
    user_input = state['user_input']
    conversation_history = state['conversation_history']
    node_history = state['node_history']
    document_history = state['document_history']
    strategy_history = state['strategy_history']
    reflection_history = state['reflection_history']
    requirements_history = state['requirements_history']
    structure_history = state['structure_history']
    latest_strategy_instruction = (state['strategy_history'][-1] if state['strategy_history'] else {"content": "No strategy history available"})['content']

    prompt = f"""
    You are an expert requirements analyst. Your task is to analyze the document structure and context to create a comprehensive, prioritized list of all information and data needed to create this document.
    You will be given the latest strategy instruction from the strategy agent: {latest_strategy_instruction}
    
    Context from previous interactions:
    {user_input}
    {conversation_history}
    {node_history}
    {document_history}
    {strategy_history}
    {reflection_history}
    {requirements_history}
    {structure_history}

    Please analyze the document requirements and provide your analysis in this format:

    # Document Requirements Analysis

    ## Priority 1 - Critical Requirements (Must Have)
    1. [Requirement Name]
       - Description: Detailed explanation
       - Source: Where this information should come from
       - Format: Expected format (numbers, text, charts, etc.)
       - Usage: Which sections will use this information
       
    2. [Next Critical Requirement]
       ...

    ## Priority 2 - Important Requirements (Should Have) 
    1. [Requirement Name]
       - Description:
       - Source:
       - Format:
       - Usage:
       ...

    ## Priority 3 - Supporting Requirements (Nice to Have)
    1. [Requirement Name]
       - Description:
       - Source:
       - Format:
       - Usage:
       ...

    ## Data Collection Order
    1. First collect: [Requirements list] - Reason: [Why these first]
    2. Then gather: [Requirements list] - Reason: [Why these second]
    3. Finally collect: [Requirements list] - Reason: [Why these last]

    ## Special Considerations
    - Dependencies: [List any requirements that depend on others]
    - Time-sensitive data: [List any data that needs to be current]
    - Verification needs: [Data that needs special verification]

    Consider:
    1. All information needed for each section
    2. Both quantitative and qualitative data
    3. Historical and current data needs
    4. Internal and external data sources
    5. Dependencies between information
    6. Time sensitivity of data points
    7. Verification requirements
    8. Format and presentation needs

    IMPORTANT:
    - Prioritize requirements clearly
    - Identify dependencies
    - Note time-sensitive elements
    - Flag verification needs
    - Highlight missing information
    - Specify data formats
    - Note collection sequence
    - Consider integration points

    Please provide your response in this JSON format:
    {{
        "message_to_agent": "Your analysis notes, missing information, clarifications needed, and recommendations about the requirements gathering process",
        "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
        "requirements": "MUST BE IN MARKDOWN FORMAT. The comprehensive requirements analysis following the structure above"
    }}
    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert requirements analyst."},
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
            "node": "doc_requirements",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify the document requirements in the requirements_history"
        })

        state["requirements_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "document_id": document_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_requirements",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_requirements agent with state: %s", json.dumps(state, indent=2))
    return state



