"""
Simplified FastAPI server for serving SAT practice questions without database dependencies.
"""

import json
import os
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SAT Practice API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to extracted questions NDJSON file
EXTRACTED_QUESTIONS_PATH = "/home/iamdankwa/SAT-Tutor-2/backend/app/pipelines/output.ndjson"

@app.get("/")
async def root():
    return {"message": "Welcome to SAT Practice API"}

@app.get("/api/v1/practice/sat-questions", response_model=List[Dict[str, Any]])
async def get_sat_questions(
    module: Optional[str] = Query(None, description="Filter by module number (1 or 2)"),
    question_type: Optional[str] = Query(None, description="Filter by question type"),
    section: Optional[str] = Query(None, description="Filter by section")
):
    """
    Get SAT questions from the NDJSON output file
    """
    try:
        # Check if the file exists
        if not os.path.exists(EXTRACTED_QUESTIONS_PATH):
            raise HTTPException(status_code=404, detail=f"Questions file not found at {EXTRACTED_QUESTIONS_PATH}")
        
        questions = []
        
        with open(EXTRACTED_QUESTIONS_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        question_data = json.loads(line)
                        
                        # Apply filters
                        if module and str(question_data.get('module')) != module:
                            continue
                        if section and question_data.get('section') != section:
                            continue
                        if question_type and question_data.get('type') != question_type:
                            continue
                        
                        # Transform the data to match frontend expectations
                        formatted_question = {
                            "id": question_data.get('id'),
                            "number": question_data.get('question_number'),
                            "module": question_data.get('module'),
                            "section": question_data.get('section'),
                            "type": question_data.get('type'),
                            "category": question_data.get('category'),
                            "content": question_data.get('stimulus', ''),
                            "choices": question_data.get('choices', {}),
                            "correctAnswer": question_data.get('correct'),
                            "explanation": "Detailed explanation would be provided here."
                        }
                        
                        questions.append(formatted_question)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {e}")
                        continue
        
        return questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing questions: {str(e)}")

@app.post("/api/v1/practice/record-progress")
async def record_practice_progress(data: Dict[str, Any]):
    """
    Mock endpoint for recording practice progress (without database)
    """
    return {
        "success": True,
        "message": f"Progress recorded successfully (mock). Topic: {data.get('topic_id')}, Correct: {data.get('correct')}"
    }

# Run with: uvicorn app.simplified_server:app --reload --host 0.0.0.0 --port 8000