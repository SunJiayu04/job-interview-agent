from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import openai
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# 把静态资源挂到 /static，不要挂在根 "/"
app.mount("/static", StaticFiles(directory="/app/frontend_build/static"), name="static")

# 根路径返回 index.html
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
async def predict(req: PredictRequest):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    prompt = build_prompt(req.role, req.level, req.count_tech, req.count_behavior, req.count_scenario)
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=800
        )
        text = resp.choices[0].message.content
        return {"raw": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
