from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_writer(state: MainState) -> MainState:
    """
    doc_writer is an AI agent that can be used to generate content for a document based on the user's requirements, context, and strategy.
    """
    logger.info("doc_writer started with state: %s", json.dumps(state, indent=2))

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
    document_id = state['document_id']
    doc_writer_history = state['doc_writer_history']

    prompt = f"""
    You are an expert content writer with deep knowledge of professional writing techniques. Your task is to generate high-quality content based on the provided context, requirements, and Andika's instructions. You can write either complete documents or specific sections as requested.

    Context from previous interactions:
    {user_input}
    {conversation_history}
    {node_history}
    {document_history}
    {strategy_history}
    {reflection_history}
    {requirements_history}
    {structure_history}

    Please write the content using the following rules::

    # Content Generation

    ## Message to agent
    [IMPORTANT: Use this section to:
    - Confirm which sections you're writing (full document or specific sections)
    - Ask for any missing information or clarifications needed
    - Request additional context or requirements if needed
    - Suggest improvements or alternatives
    - Highlight any potential issues or dependencies]

    ## Writing Approach
    ### Content Scope
    - Writing Task: [Full document/Specific section(s)]
    - Target Sections: [List of sections to be written]
    - Integration Points: [How this connects with existing content]
    - Dependencies: [Required information or prerequisites]

    ### Strategic Elements
    - Tone and Voice: [Based on user preferences]
    - Style Approach: [Formal/Technical/Conversational]
    - Audience Level: [Technical expertise required]
    - Key Objectives: [What this content should achieve]

    ## Generated Content
    [Either full document or requested sections, maintaining consistent structure]

    ### [Section Name]
    [Content following structure and requirements]

    ### [Next Section]
    [Content following structure and requirements]

    [Continue for all required sections...]

    ## Content Validation
    ### Quality Checks
    - Alignment: [Matches requirements and structure]
    - Completeness: [All required elements included]
    - Technical Accuracy: [Domain-specific correctness]
    - Style Consistency: [Maintains required tone]

    ### Enhancement Suggestions
    - Potential Improvements: [Areas that could be strengthened]
    - Additional Elements: [Suggested additions]
    - Integration Notes: [How to blend with other sections]
    - Next Steps: [What needs to happen next]

    Consider these principles:
    1. Write only the requested sections
    2. Maintain consistency with existing content
    3. Follow established style and tone
    4. Ensure technical accuracy
    5. Support document objectives
    6. Enable smooth integration
    7. Flag any missing requirements
    8. Suggest improvements proactively

    Your content should:
    1. Match exactly what was requested (full document or specific sections)
    2. Integrate seamlessly with other content
    3. Follow user's preferred style
    4. Meet all specified requirements
    5. Support overall document goals
    6. Maintain professional standards
    7. Enable desired outcomes
    8. Flag any potential issues

    IMPORTANT: 
    - Clearly state in Message to Agent if you need any additional information
    - Specify which sections you're writing
    - Highlight any integration considerations with other sections
    - Ask for clarification if the scope is unclear

    Please provide your response in this JSON format:
    {
        "message_to_agent": "Your analysis of the writing task, clarifications needed, and any other important notes",
        "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
        "document_content": "MUST BE IN MARKDOWN FORMAT. The generated document content following all specified requirements and structure"
    }
    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert writer."},
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
            "node": "doc_writer",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify user reflections in the reflection_history"
        })

        state["doc_writer_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "document_id": document_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_writer",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_reflections agent with state: %s", json.dumps(state, indent=2))
    return state



