from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import Optional, List
from dotenv import load_dotenv
import os
from agents.tutor_agent import TutorAgent

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Constants for validation
MAX_QUERY_LENGTH = 4000
MIN_QUERY_LENGTH = 1

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        if len(v.strip()) < MIN_QUERY_LENGTH:
            raise ValueError("Query is too short")
            
        if len(v) > MAX_QUERY_LENGTH:
            raise ValueError(f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters")
        
        return v.strip()

class ConversationRequest(BaseModel):
    user_id: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    
class QueryResponse(BaseModel):
    response: str
    conversation_id: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
tutor_agent = TutorAgent(GEMINI_API_KEY)

@app.post("/conversations", response_model=ConversationResponse)
async def create_conversation(request: ConversationRequest):
    """Create a new conversation"""
    try:
        conversation_id = tutor_agent.create_conversation(request.user_id)
        return ConversationResponse(conversation_id=conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@app.post("/ask", response_model=QueryResponse)
async def ask_tutor(request: QueryRequest):
    """Ask a question to the tutor with optional conversation context"""
    try:
        response, conversation_id = tutor_agent.handle_query(request.query, request.conversation_id)
        return QueryResponse(response=response, conversation_id=conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@app.get("/conversations")
async def list_conversations(user_id: Optional[str] = None):
    """List all conversations, optionally filtered by user"""
    try:
        conversations = tutor_agent.list_conversations(user_id)
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation information and history"""
    try:
        conversation_info = tutor_agent.get_conversation_info(conversation_id)
        if not conversation_info:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        history = tutor_agent.get_conversation_history(conversation_id)
        
        return {
            "conversation_info": conversation_info,
            "history": history
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        success = tutor_agent.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Visit /static/index.html to use the Tutor Agent"}