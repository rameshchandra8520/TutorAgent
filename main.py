from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from agents.tutor_agent import TutorAgent

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
tutor_agent = TutorAgent(GEMINI_API_KEY)

@app.post("/ask")
async def ask_tutor(request: QueryRequest):
    try:
        response = tutor_agent.handle_query(request.query)
        return {"response": response}
    except Exception as e:
        return {"error": f"Failed to process query: {str(e)}"}