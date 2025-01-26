from typing import Dict, Any
from datetime import datetime, timezone
import json
import uuid
from shared_services.llm import call_llm_api
from shared_services.shared_types import MainState
from shared_services.extract_and_parse_json import extract_and_parse_json
from shared_services.logger_setup import setup_logger

logger = setup_logger()

def doc_strategy(state: MainState) -> MainState:
    """
    doc_strategy is an AI agent that will manage the overall strategy for the document authoring process.
    It will generate & manage/update the stratergy by handing off to the agents below:
     1. doc_reflections
     2. doc_requirements
     3. doc_structure
    """

    logger.info("doc_strategy started with state: %s", json.dumps(state, indent=2))

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

    prompt = f"""
You are an expert document strategy coordinator. Your task is to analyze the current state and determine which strategy components need updates or creation. You'll coordinate between three strategy agents:
1. doc_reflections - Analyzes user behavior and preferences
2. doc_requirements - Determines document requirements
3. doc_structure - Creates document structure and outline

Context from previous interactions:
{user_input}
{conversation_history}
{node_history}
{document_history}
{strategy_history}
{reflection_history}
{requirements_history}
{structure_history}

Please analyze the strategic needs considering:

1. Document Complexity Assessment
   - Document size and scope
   - Technical complexity
   - Audience sophistication
   - Time constraints
   - Resource requirements
   - Integration needs
   - Update frequency
   - Critical dependencies

2. Strategy Component Analysis
   A. User Reflections Status
      - Existing user profile completeness
      - Recent behavioral changes
      - New preference indicators
      - Communication pattern shifts
      - Expertise level changes
      
   B. Requirements Status
      - Current requirements coverage
      - New requirements indicators
      - Changed priorities
      - Scope modifications
      - Timeline updates
      
   C. Structure Status
      - Structure completeness
      - Format appropriateness
      - Section dependencies
      - Integration points
      - Navigation clarity

3. Update Triggers
   - New user input
   - Changed requirements
   - Timeline modifications
   - Scope adjustments
   - Format changes
   - Priority shifts
   - Resource updates
   - Integration needs

4. Strategy Optimization
   - Process efficiency
   - Resource utilization
   - Quality assurance
   - Timeline management
   - Risk mitigation
   - Change control
   - Version management
   - Integration planning

Consider these factors:
1. Document complexity vs. strategy needs
2. User expertise vs. guidance required
3. Timeline vs. process depth
4. Resource availability vs. requirements
5. Change impact vs. update necessity
6. Integration complexity vs. coordination needs
7. Risk level vs. control requirements
8. Quality needs vs. process depth

IMPORTANT:
- Assess if full strategy is needed
- Identify critical updates required
- Prioritize agent actions
- Note dependencies
- Consider resource constraints
- Flag urgent needs
- Maintain consistency
- Enable efficient handoffs

Please provide your response in this JSON format:
{{  
    "message_to_agent": "Your analysis of the strategic needs and coordination recommendations",
    "message_to_user": "Your message to the user/client/human. Leave this blank if you have no message to the user/client/human",
    "strategy_actions": {{
        "needs_strategy": true/false,
        "explanation": "Detailed explanation of why strategy is or isn't needed",
        "priority_order": "["agent_name1", "agent_name2", "agent_name3"]",
        "actions": [
            {{
                "agent": "doc_reflections/doc_requirements/doc_structure",
                "action": "create/update/skip",
                "priority": "high/medium/low",
                "reason": "Why this action is needed",
                "focus_areas": "["specific aspects to focus on"]",
                "dependencies": "["any dependencies"]",
                "instructions": "Specific instructions for the agent"
            }}
        ],
        "coordination_notes": "Notes about coordination between agents",
        "risk_factors": "["potential risks to consider"]",
        "success_criteria": "["criteria for successful strategy completion"]"
    }}
}}
"""
     # Prepare messages for LLM API call
    messages = [
        {"role": "system", "content": "You are an expert document strategy coordinator."},
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
            "node": "doc_strategy",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Use the reponse id to identify strategy in the strategy_history"
        })

        state["strategy_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": parsed_response
        })

    except Exception as e:
        logger.error("Error in LLM response parsing: %s", str(e))
        state["node_history"].append({
            "role": "AI_AGENT",
            "node": "doc_strategy",
            "conversation_id": state["conversation_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_id": response_id,
            "content": "Apologies, I encountered an error. Please try again."
               
        })

    # Log final state
    logger.info("Completed doc_strategy agent with state: %s", json.dumps(state, indent=2))
    return state



