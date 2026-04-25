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
    job_description: str = ""
    my_experience: str = ""

def build_prompt(role, level, ct, cb, cs, job_description, my_experience):
    return f"""
You are an expert recruiter and interview coach. Given the inputs below, produce a practical, structured interview preparation package tailored to the Job Description (JD) and the candidate's supplied experience.

Inputs:
- Role: {role}
- Level: {level}
- Job Description:
{job_description}

- Candidate experience summary:
{my_experience}

Task:
1) Produce a "Role Competency Map": list 6-10 key competencies/skills required by the JD. For each competency include (a) short description, (b) evidence to look for in answers or resume, and (c) suggested difficulty/importance (High/Medium/Low).

2) Produce "Likely Interview Questions": grouped by Technical / Behavioral / Scenario. For each question include:
   - the question text
   - difficulty tag (easy/medium/hard)
   - 1-line scoring rubric / what a strong answer demonstrates

3) Produce "Best Matching Experience" from the candidate input: highlight 3-5 bullet points that rephrase the candidate's experience to emphasize fit with the JD (make them concise resume-style bullets).

4) Provide "STAR Answer Outline" for 2-3 top behavioral/scenario questions: for each, provide structured bullet points following STAR (Situation, Task, Action, Result) that the candidate can use to craft answers.

5) Provide "Follow-up Questions and Risk Points": list follow-up probes the interviewer should ask and any risk/gap items to watch for (e.g., missing tool experience, short tenures, lack of scale experience).

Format:
- Be concise, practical, and specific to the JD and candidate experience.
- Return the package as plain text with clear labeled sections (1..5). Do NOT include meta commentary or explanation about your instructions.
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
            req.count_scenario,
            req.job_description,
            req.my_experience
        )

        # Call Gemini (using your existing genai client)
        # Adjust model name if needed per your account
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # The genai response object shape may vary; use .text if available
        text = None
        try:
            text = response.text
        except Exception:
            try:
                # fallback: inspect choices or content field
                text = getattr(response, "output", None) or str(response)
            except Exception:
                text = str(response)

        print("Gemini response received", flush=True)

        return {"raw": text}

    except Exception as e:
        print("Error in /predict:", repr(e), flush=True, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail="Internal server error; check server logs for details"
        )
