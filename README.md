# job-interview-agent (MVP)

Prerequisites: Docker, Git, GitHub repo, Render account, OpenAI API key.

Local run (backend):
- cd backend
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt
- export OPENAI_API_KEY=your_key
- uvicorn backend.main:app --reload --port 8000

Frontend dev:
- cd frontend
- npm install
- npm start

Build & run with Docker:
- docker build -t job-interview-agent .
- docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8000:8000 job-interview-agent

Render deploy summary:
1. Create new Web Service on Render (Docker).
2. Connect your GitHub repo and choose branch.
3. Set Environment Variable OPENAI_API_KEY in Render settings.
4. Deploy.

API:
POST /predict
Body JSON: { "role":"Backend Engineer", "level":"mid" }
Response: {"raw": "<LLM output JSON string>"}
