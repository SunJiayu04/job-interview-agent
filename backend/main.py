from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import openai
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import traceback
import sys

# 从环境变量读取 OpenAI key（不要把 key 写进代码）
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# 把静态资源挂到 /static（不要挂在根 "/")
app.mount("/static", StaticFiles(directory="/app/frontend_build/static"), name="static")

# 根路径返回 index.html
@app.get("/")
async def root():
    index_path = "/app/frontend_build/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Frontend not built"}

# 请求模型
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

# POST /predict 路由（包含详细日志/traceback 用于调试）
@app.post("/predict")
async def predict(req: PredictRequest, request: Request):
    try:
        # 打印收到的原始请求体（可在 Render 日志看到）
        body = await request.json()
        print("Received request body:", body, flush=True)

        # 检查 OPENAI API KEY 是否设置
        if not openai.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        # 生成 prompt 并调用模型
        prompt = build_prompt(req.role, req.level, req.count_tech, req.count_behavior, req.count_scenario)

        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=800
        )

        # 调试打印部分返回（避免泄露敏感信息）
        try:
            print("OpenAI response keys:", list(resp.keys()) if hasattr(resp, "keys") else "no keys", flush=True)
        except Exception:
            pass

        # 解析返回文本
        text = resp.choices[0].message.content
        return {"raw": text}

    except Exception as e:
        # 把错误和完整 traceback 打到 stderr（Render 日志可见）
        print("Error in /predict:", repr(e), flush=True, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # 返回给前端简短信息，具体细节查看日志
        raise HTTPException(status_code=500, detail="Internal server error; check server logs for details")
