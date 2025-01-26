from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_researcher(state: MainState) -> MainState:
    """
    doc_requirements is an AI agent that can be used to generate document requirements i.e what is needed to generate the document based on user requirements and context.
    """
    logger.info("doc_requirements started with state: %s", json.dumps(state, indent=2))

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
    research_history = state['research_history']
    document_id = state['document_id']
   
    prompt = f"""
    You are an expert research strategist and information analyst. Your task is to analyze the document requirements and context to identify information gaps, determine research needs, and create a comprehensive research plan. Focus on both internal knowledge (from users) and external sources (internet research).
   
    
    Context from previous interactions:
    {user_input}
    {conversation_history}
    {node_history}
    {document_history}
    {strategy_history}
    {reflection_history}
    {requirements_history}
    {structure_history}

    Please analyze research needs in these categories:

    1. Information Gap Analysis
       - Review existing information in conversation history
       - Compare against document requirements
       - Identify missing critical information
       - Flag unclear or incomplete data
       - Note areas needing verification

    2. Research Categories
       A. Internal Knowledge (User/Organization Specific)
          - Company-specific processes
          - Internal policies
          - Team experiences
          - Project specifics
          - Historical context
          - Strategic goals
          - Performance metrics
          - Stakeholder preferences

       B. External Research (Internet/Public Sources)
          - Industry trends
          - Market data
          - Competitor analysis
          - Technical standards
          - Best practices
          - Case studies
          - Statistical data
          - Academic research

       C. Hybrid Information (Needs Both Sources)
          - Implementation strategies
          - Performance benchmarks
          - Success metrics
          - Risk assessments
          - Impact analysis
          - Compliance requirements

    3. Research Prioritization
       - Critical path items
       - Time-sensitive information
       - Dependency-based priorities
       - Effort vs. impact assessment
       - Resource availability
       - Access constraints

    Consider:
    1. Information reliability requirements
    2. Time constraints for gathering data
    3. Verification needs
    4. Source accessibility
    5. Data freshness requirements
    6. Integration complexity
    7. Resource availability
    8. Legal/compliance considerations

    IMPORTANT:
    - Prioritize critical information gaps
    - Consider source reliability
    - Note time sensitivity
    - Flag verification requirements
    - Consider access constraints
    - Identify potential blockers
    - Note interdependencies
    - Plan for contingencies

    Please provide your response in this JSON format:
    {{
        "message_to_agent": "Your analysis of research needs, strategy recommendations, and any important considerations about the research process",
        "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
        "research_plan": {{
            "internal_queries": [
                {{
                    "question": "Specific question to ask user/organization",
                    "source": "human", 
                    "explanation": "Why this information is needed and how it will be used",
                    "priority": "high/medium/low",
                    "time_sensitivity": "immediate/flexible/long_term"
                }}
            ],
            "external_queries": [
                {{
                    "question": "Specific question to research online",
                    "source": "internet",
                    "explanation": "Why this information is needed and how it will be used", 
                    "priority": "high/medium/low",
                    "suggested_sources": ["type of sources to consult"]
                }}
            ],
            "hybrid_queries": [
                {{
                    "question": "Question requiring both internal and external input",
                    "source": "human_internet",
                    "explanation": "Why both sources are needed and how information will be integrated",
                    "priority": "high/medium/low",
                    "internal_aspects": ["what to ask users"],
                    "external_aspects": ["what to research"]
                }}
            ]
        }}
    }}

    
    """
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert research strategist and informationmanalyst."},
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
            "node": "doc_researcher",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify the research plan in the research_history"
        })

        state["research_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "document_id": document_id,
            "response_id": response_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_researcher",
            "conversation_id": conversation_id,
            "document_id": document_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_researcher agent with state: %s", json.dumps(state, indent=2))
    return state



