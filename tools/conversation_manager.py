import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}
        logger.info("Conversation Manager initialized")
    
    def create_conversation(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "history": [],
            "metadata": {}
        }
        
        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id
    
    def add_interaction(self, conversation_id: str, query: str, response: str, agent_type: Optional[str] = None):
        """Add a query-response interaction to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        interaction = {
            "timestamp": datetime.now(),
            "query": query,
            "response": response,
            "agent_type": agent_type
        }
        
        self.conversations[conversation_id]["history"].append(interaction)
        self.conversations[conversation_id]["last_activity"] = datetime.now()
        
        logger.info(f"Added interaction to conversation {conversation_id}")
    
    def get_conversation_history(self, conversation_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get the history for a specific conversation"""
        if conversation_id not in self.conversations:
            return []
        
        history = self.conversations[conversation_id]["history"]
        
        if limit:
            return history[-limit:]
        return history
    
    def get_formatted_history(self, conversation_id: str, limit: Optional[int] = 3) -> str:
        """Get formatted history string for AI context"""
        history = self.get_conversation_history(conversation_id, limit)
        
        if not history:
            return ""
        
        formatted_history = []
        for interaction in history:
            formatted_history.append(f"Q: {interaction['query']}")
            formatted_history.append(f"A: {interaction['response']}")
        
        return "\n".join(formatted_history)
    
    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        return conversation_id in self.conversations
    
    def get_conversation_info(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation metadata"""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[Dict]:
        """List all conversations, optionally filtered by user"""
        conversations = []
        
        for conv_id, conv_data in self.conversations.items():
            if user_id is None or conv_data.get("user_id") == user_id:
                conversations.append({
                    "id": conv_id,
                    "user_id": conv_data.get("user_id"),
                    "created_at": conv_data["created_at"],
                    "last_activity": conv_data["last_activity"],
                    "interaction_count": len(conv_data["history"])
                })
        
        # Sort by last activity (most recent first)
        conversations.sort(key=lambda x: x["last_activity"], reverse=True)
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False
    
    def clear_old_conversations(self, days: int = 30):
        """Clear conversations older than specified days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        conversations_to_delete = []
        
        for conv_id, conv_data in self.conversations.items():
            if conv_data["last_activity"] < cutoff_date:
                conversations_to_delete.append(conv_id)
        
        for conv_id in conversations_to_delete:
            self.delete_conversation(conv_id)
        
        logger.info(f"Cleared {len(conversations_to_delete)} old conversations")
        return len(conversations_to_delete) 