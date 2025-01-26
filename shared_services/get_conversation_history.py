import os
import json
from datetime import datetime
from typing import Dict, Any
from .db import get_postgres_connection
from .logger_setup import setup_logger
from psycopg2.extras import RealDictCursor


logger = setup_logger()

def get_conversation_history(
    user_id: str, 
    session_id: str,
    conversation_id: str,
    limit: int,
) -> Dict[str, Any]:
    """
    Extract conversation_history, node_history, and structure_history from state column
    """
    conn = get_postgres_connection("conversations")
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    state->'conversation_history' as conversation_history,
                    state->'node_history' as node_history,
                    state->'structure_history' as structure_history,
                    state->'requirements_history' as requirements_history,
                    state->'reflection_history' as reflection_history,
                    state->'research_history' as research_history,
                    state->'strategy_history' as strategy_history
                FROM andika_conversations 
                WHERE user_id = %s 
                AND session_id = %s 
                ORDER BY log_timestamp DESC
                LIMIT %s;
            """, (user_id, session_id, limit))
            
            results = cur.fetchall()
            
            if not results:
                logger.info(f"No conversations found for user_id: {user_id}")
                return {
                    "status": "no_data",
                    "conversation_history": [],
                    "node_history": [],
                    "structure_history": [],
                    "requirements_history": [],
                    "reflection_history": [],
                    "research_history": [],
                    "strategy_history": []
                }
            
            # Extract histories
            conversations = []
            node_conversations = []
            structure_conversations = []
            requirements_conversations = []
            reflection_conversations = []
            research_conversations = []
            strategy_conversations = []
            for result in results:
                if result['conversation_history']:
                    conversations.extend(result['conversation_history'])
                if result['node_history']:
                    node_conversations.extend(result['node_history'])
                if result['structure_history']:
                    structure_conversations.extend(result['structure_history'])
                if result['requirements_history']:
                    requirements_conversations.extend(result['requirements_history'])
                if result['reflection_history']:
                    reflection_conversations.extend(result['reflection_history'])
                if result['research_history']:
                    research_conversations.extend(result['research_history'])
                if result['strategy_history']:
                    strategy_conversations.extend(result['strategy_history'])


            # Sort with error handling
            def safe_sort(items):
                try:
                    return sorted(
                        items,
                        key=lambda x: datetime.fromisoformat(x.get('timestamp', datetime.now().isoformat())),
                        reverse=True  # Newest first
                    )
                except Exception as e:
                    logger.warning(f"Error sorting items: {e}")
                    return items

            return {
                "status": "success",
                "conversation_history": safe_sort(conversations),
                "node_history": safe_sort(node_conversations),
                "structure_history": safe_sort(structure_conversations),
                "requirements_history": safe_sort(requirements_conversations),
                "reflection_history": safe_sort(reflection_conversations),
                "research_history": safe_sort(research_conversations),
                "strategy_history": safe_sort(strategy_conversations)
            }
            
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return {
            "status": "error",
            "conversation_history": [],
            "node_history": [],
            "structure_history": [],
            "requirements_history": [],
            "reflection_history": [],
            "research_history": [],
            "strategy_history": []
        }
    finally:
        conn.close()