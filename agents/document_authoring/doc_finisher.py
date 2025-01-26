from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_finisher(state: MainState) -> MainState:
    """
    doc_finisher is an AI agent that can be used to finish off documents i.e proofreading, formatting, consistency checks, etc.
    """
    logger.info("doc_finisher started with state: %s", json.dumps(state, indent=2))

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
    latest_document = document_history[-1]

    prompt = f"""
    You are an expert document editor and proofreader with exceptional attention to detail. Your task is to perform comprehensive quality assurance on documents or sections, ensuring they meet the highest professional standards.
    The document you are reviewing is : {latest_document}
    Context from previous interactions:
    {user_input}
    {conversation_history}
    {node_history}
    {document_history}
    {strategy_history}
    {reflection_history}
    {requirements_history}
    {structure_history}

    Please provide your analysis in this format:

    # Document Quality Analysis

    ## Message to Andika
    [IMPORTANT: Use this section to:
    - Confirm what you're reviewing (full document or specific sections)
    - Highlight critical issues found
    - Request clarifications about style guides or requirements
    - Suggest major structural improvements
    - Flag any consistency issues between sections]

    ## Document Review
    ### Scope Assessment
    - Review Type: [Full document/Specific sections]
    - Sections Reviewed: [List of sections]
    - Integration Check: [How sections flow together]
    - Completeness Check: [Missing elements or sections]

    ### Structural Analysis
    - Document Flow: [Logical progression of ideas]
    - Section Transitions: [Smoothness between sections]
    - Information Hierarchy: [Proper organization of content]
    - Content Balance: [Distribution of information]

    ## Quality Checks
    ### Technical Accuracy
    - Grammar and Syntax: [Issues found]
    - Spelling and Punctuation: [Issues found]
    - Technical Terms: [Consistency in usage]
    - Formatting: [Style guide compliance]

    ### Content Consistency
    - Terminology Usage: [Consistent terms throughout]
    - Voice and Tone: [Consistency across sections]
    - Style Adherence: [Following style guide]
    - Numbering/Bullets: [Consistent formatting]

    ### Document Standards
    - Brand Guidelines: [Compliance check]
    - Citation Style: [Proper references]
    - Visual Elements: [Image/table formatting]
    - Layout Standards: [Document formatting]

    ## Detailed Findings
    ### Critical Issues
    - High Priority: [Must-fix issues]
    - Medium Priority: [Should-fix issues]
    - Low Priority: [Nice-to-fix issues]
    - Style Suggestions: [Optional improvements]

    ### Section-Specific Notes
    [For each section reviewed:]
    - Section Name: [Issues and recommendations]
    - Integration Points: [Connection with other sections]
    - Completeness: [Missing elements]
    - Enhancement Suggestions: [Improvements]

    ## Integration Assessment
    ### Cross-References
    - Internal Links: [Proper section references]
    - External Links: [Valid citations/sources]
    - Figure References: [Correct numbering]
    - Table References: [Proper formatting]

    ### Document Cohesion
    - Narrative Flow: [Story consistency]
    - Argument Structure: [Logical progression]
    - Key Messages: [Consistent throughout]
    - Supporting Elements: [Proper integration]

    ## Final Recommendations
    ### Required Changes
    - Critical Fixes: [Must implement]
    - Technical Corrections: [Grammar/spelling]
    - Structural Adjustments: [Organization]
    - Format Updates: [Layout/style]

    ### Enhancement Suggestions
    - Content Improvements: [Clarity/impact]
    - Structure Refinements: [Better flow]
    - Style Enhancements: [Better presentation]
    - Additional Elements: [Suggested additions]

    Consider these aspects:
    1. Overall document coherence
    2. Section-to-section transitions
    3. Style guide compliance
    4. Technical accuracy
    5. Content completeness
    6. Visual consistency
    7. Reference accuracy
    8. Audience appropriateness

    Quality standards to maintain:
    1. Professional polish
    2. Technical precision
    3. Logical flow
    4. Consistent voice
    5. Clear messaging
    6. Proper formatting
    7. Accurate references
    8. Engaging presentation

    IMPORTANT:
    - Make all possible corrections
    - Maintain original meaning
    - Flag issues needing input
    - Keep document structure
    - Preserve key terminology
    - Note required decisions
    - Highlight missing elements

    Please provide your response in this JSON format:
    {{"message_to_agent": "List of all changes made, issues requiring attention, and recommendations",
     "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
     "document_content": "MUST BE IN MARKDOWN FORMAT. The complete corrected document/section with all implementable fixes applied"}}
     


    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert document editor and proofreader."},
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
            "node": "doc_finisher",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify user reflections in the reflection_history"
        })

        state["doc_finisher_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "document_id": document_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_finisher",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_finisher agent with state: %s", json.dumps(state, indent=2))
    return state



# Sample usage of the agent