AI Text Summarizer
Project Overview

AI Text Summarizer is a FastAPI-based backend service that provides AI-powered text summarization using Gemini API.
It supports synchronous and asynchronous summarization, caching, and task management.

Live Project Link - https://ai-text-summarizer-1-project.onrender.com

Features

Synchronous Summarization: Instant results via /summarize

Asynchronous Summarization: Background tasks via /summarize/async

Task Result Retrieval: /tasks/{task_id}

Health Check: /health

Redis Caching & Stats: /stats

OpenAPI/Swagger Docs: /docs or /redoc

Tech Stack

Backend: FastAPI

AI Model: Gemini (generativeai SDK)

Cache/Task Storage: Redis

Task Queue: Asyncio / Celery

Docs: OpenAPI 3.1.0 / Swagger

Python Version: 3.10+

Quick Installation (Local)
git clone https://github.com/your-username/ai-text-summarizer.git
cd ai-text-summarizer
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
pip install -r requirements.txt


Create .env:

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2
API_V1_STR=/api/v1
PROJECT_NAME=AI Text Summarizer
REDIS_URL=redis://localhost:6379


Start Redis server locally:

redis-server


Run FastAPI server:

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


Docs:

Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

API Endpoints & Usage
1️⃣ Synchronous Summarization

Endpoint: POST /api/v1/summarize

Purpose: Generate summary instantly for short text

Request Example:

{
  "text": "Your text here...",
  "summary_type": "brief",
  "max_words": 50
}


Response Example:

{
  "summary": "Generated summary...",
  "original_length": 500,
  "summary_length": 50,
  "compression_ratio": 0.1,
  "processing_time": 1.23
}

2️⃣ Asynchronous Summarization

Endpoint: POST /api/v1/summarize/async

Purpose: Submit large text for background processing

Request Example:

{
  "text": "Your large text...",
  "summary_type": "brief",
  "max_words": 100
}


Response Example:

{
  "task_id": "abc123",
  "status": "pending",
  "message": "Task submitted successfully"
}

3️⃣ Get Task Result

Endpoint: GET /api/v1/tasks/{task_id}

Purpose: Fetch result of asynchronous summarization

Response Example:

{
  "task_id": "abc123",
  "status": "completed",
  "result": {
    "summary": "...",
    "original_length": 500,
    "summary_length": 50,
    "compression_ratio": 0.1,
    "processing_time": 1.23
  },
  "created_at": "2025-08-29T10:00:00Z",
  "completed_at": "2025-08-29T10:01:00Z",
  "error": null
}

4️⃣ Health Check

Endpoint: GET /api/v1/health

Purpose: Check if the service is running

Response Example:

{
  "status": "running",
  "timestamp": "2025-08-29T10:05:00Z",
  "version": "1.0.0"
}

5️⃣ Service Stats

Endpoint: GET /api/v1/stats

Purpose: Get Redis-stored statistics (total tasks, completed, failed, pending)

Response Example:

{
  "total_tasks": 100,
  "completed": 80,
  "pending": 15,
  "failed": 5
}

Project Structure
app/
├── main.py                  # FastAPI entrypoint
├── config.py                # Environment/config settings
├── api/
│   └── routes.py            # API routes (sync, async, health, stats)
├── services/
│   ├── ai_service.py        # Gemini AI interaction (sync/async)
│   └── cache_service.py     # Redis caching & stats
├── workers/
│   └── celery_workers.py    # Background task workers for async summarization
├── models/
  

Docker Setup (Optional)

Dockerfile

FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


Build Docker image:

docker build -t ai-text-summarizer .


Run container (ensure Redis is running):

docker run -d -p 8000:8000 --name ai-text-summarizer ai-text-summarizer

Usage Notes

Use sync endpoint for short text or testing

Use async endpoint for large documents

Poll task results using /tasks/{task_id}

Monitor Redis stats using /stats

License

MIT License © 2025
