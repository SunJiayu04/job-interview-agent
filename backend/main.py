from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import traceback
import sys
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google import genai

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

app = FastAPI()

app.mount("/static", StaticFiles(directory="/app/frontend_build/static"), name="static")

@app.get("/")
async def root():
    index_path = "/app/frontend_build/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Frontend not built"}

class PredictRequest(BaseModel):
    role: str
    level: str = "mid"
    count_tech: int = 2
    count_behavior: int = 2
    count_scenario: int = 4

def build_prompt(role, level, ct, cb, cs):
    return f"""
You are an expert recruiter. Given the role: "{role}", level: "{level}", generate {ct} technical interview questions, {cb} behavioral questions, and {cs} scenario-based questions.
Output JSON array of objects: {{ "id": int, "type": "technical|behavior|scenario", "question": "...", "difficulty": "easy|medium|hard", "answer_outline": "..." }}.
No extraneous text.
"""

@app.post("/predict")
async def predict(req: PredictRequest, request: Request):
    try:
        try:
            body = await request.json()
            print("Received request body:", body, flush=True)
        except Exception:
            print("Could not read raw request body", flush=True)

        if not GEMINI_KEY:
            raise RuntimeError("GEMINI_API_KEY not set in environment")

        prompt = build_prompt(
            req.role,
            req.level,
            req.count_tech,
            req.count_behavior,
            req.count_scenario
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        print("Gemini response received", flush=True)

        return {"raw": text}

    except Exception as e:
        print("Error in /predict:", repr(e), flush=True, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail="Internal server error; check server logs for details"
        )
