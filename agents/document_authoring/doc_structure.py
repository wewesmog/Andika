from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_structure(state: MainState) -> MainState:
    """
    doc_structure is an AI agent that can be used to generate document structure based on user requirements and context.
    """
    logger.info("doc_structure started with state: %s", json.dumps(state, indent=2))

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
    You are an expert document architect and outlining specialist. Your task is to create a comprehensive, detailed document structure based on the provided context and requirements.
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

    Please create an exhaustive document outline that includes:

    1. Document Overview
       - Target audience
       - Purpose and objectives
       - Expected outcomes
       - Recommended tone and style
       - Document length and format specifications

    2. Detailed Structure
       - Every major section with clear titles
       - All subsections with descriptive headings
       - Bullet points of key topics to cover in each section
       - Specific guidance on what content is needed
       - Recommended word count per section
       - Suggested visual elements (tables, charts, images)

    3. Content Requirements for Each Section
       - Key points to address
       - Required data or research
       - Examples or case studies needed
       - Citations or references required
       - Special formatting requirements

    4. Technical Specifications
       - Document format (Word, PDF, etc.)
       - Page layout (margins, columns)
       - Typography (fonts, sizes, spacing)
       - Visual elements guidelines
       - Citation style

    5. Additional Elements
       - Front matter (cover, table of contents)
       - Executive summary requirements
       - Appendices needed
       - Glossary requirements
       - Index specifications

    Consider while creating structure:
    1. Logical flow of information
    2. User requirements and context
    3. Content dependencies
    4. Integration points
    5. Formatting consistency
    6. Navigation ease
    7. Content accessibility
    8. Overall coherence

    IMPORTANT:
    - Ensure clear hierarchy
    - Maintain logical flow
    - Consider user needs
    - Include all necessary sections
    - Specify formatting requirements
    - Note dependencies
    - Consider navigation
    - Enable easy updates

    Please provide your response in this JSON format:
    {{
        "message_to_agent": "Your analysis notes, missing information, clarifications needed, and recommendations about the document structure",
        "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
        "structure": "MUST BE IN MARKDOWN FORMAT. The comprehensive document structure following the outline format above"
    }}
    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are a document structure expert. Given the context below, generate a document structure (outline of a document) that will help other agents generate a document."},
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
            "node": "doc_structure",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify the document structure in the structure_history"
        })

        state["structure_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_structure",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_structure agent with state: %s", json.dumps(state, indent=2))
    return state



