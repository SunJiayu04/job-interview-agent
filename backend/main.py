from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import traceback
import sys
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 使用新版 OpenAI 客户端
from openai import OpenAI

# 优先从环境读取 key（不要在代码中写死 key）
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# 初始化客户端（如果为空，后面会报错并在日志中显示）
client = OpenAI(api_key=OPENAI_KEY)

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

# 请求模型的 Pydantic 模型
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
        # 打印收到的原始请求体（在 Render 日志可见）
        try:
            body = await request.json()
            print("Received request body:", body, flush=True)
        except Exception:
            print("Could not read raw request body", flush=True)

        # 检查 OPENAI key
        if not OPENAI_KEY:
            raise RuntimeError("OPENAI_API_KEY not set in environment")

        prompt = build_prompt(req.role, req.level, req.count_tech, req.count_behavior, req.count_scenario)

        # 使用新版 OpenAI 客户端调用 chat completions
        # 请根据你的帐号权限选择模型（示例使用 gpt-4o-mini）
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert recruiter who generates interview questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )

        # 打印调试信息（不包含敏感 key）
        try:
            print("OpenAI response type:", type(response), flush=True)
            # 如果 response 是 dict-like，也可打印 keys
            if hasattr(response, "choices"):
                print("OpenAI choices length:", len(response.choices), flush=True)
        except Exception:
            pass

        # 解析结果
        # 新版 SDK 的结构与版本可能稍有差异，这里尝试兼容访问
        text = None
        try:
            # 常见访问方式
            text = response.choices[0].message.content
        except Exception:
            try:
                # fallback: some SDKs return content in response.choices[0].text
                text = response.choices[0].text
            except Exception:
                # 最后 fallback 把整个 response 转为字符串
                text = str(response)

        return {"raw": text}

    except Exception as e:
        # 打印完整 traceback 到 stderr，Render 日志能看到
        print("Error in /predict:", repr(e), flush=True, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        # 返回给前端简短提示（具体细节查看日志）
        raise HTTPException(status_code=500, detail="Internal server error; check server logs for details")
