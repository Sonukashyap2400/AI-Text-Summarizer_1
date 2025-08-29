from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import time

from app.models import (
    SummarizeRequest,
    SummarizeResponse,
    TaskSubmitRequest,
    TaskResponse,
    TaskResultResponse,
    HealthCheck,
)
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service
from app.workers.celery_worker import summarize_text_task
from app.config import settings


router = APIRouter()

# Simple in-memory rate limiting
request_counts = {}


def rate_limit_check(client_ip: str):
    """Basic rate limiting per client IP."""
    current_time = time.time()

    if client_ip not in request_counts:
        request_counts[client_ip] = []

    # Remove old requests outside the window
    request_counts[client_ip] = [
        req_time
        for req_time in request_counts[client_ip]
        if current_time - req_time < settings.RATE_LIMIT_WINDOW
    ]

    if len(request_counts[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    request_counts[client_ip].append(current_time)


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """Synchronous text summarization endpoint."""
    try:
        # Check cache first
        cached_result = await cache_service.get(
            request.text, request.summary_type.value, request.max_words
        )
        if cached_result:
            return SummarizeResponse(**cached_result)

        # Generate new summary
        result = await ai_service.summarize_text(
            request.text, request.summary_type, request.max_words
        )

        # Cache the result
        await cache_service.set(
            request.text, request.summary_type.value, result.dict(), request.max_words
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize/async", response_model=TaskResponse)
async def submit_summarization_task(request: TaskSubmitRequest):
    """Submit text summarization task for background processing."""
    try:
        task = summarize_text_task.delay(
            request.text, request.summary_type.value, request.max_words
        )
        return TaskResponse(
            task_id=task.id,
            status="pending",
            message="Task submitted successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    """Get the result of a background summarization task."""
    try:
        task = summarize_text_task.AsyncResult(task_id)

        if task.state == "PENDING":
            return TaskResultResponse(
                task_id=task_id,
                status="pending",
                created_at=datetime.utcnow(),
            )

        elif task.state == "PROCESSING":
            return TaskResultResponse(
                task_id=task_id,
                status="processing",
                created_at=datetime.utcnow(),
            )

        elif task.state == "SUCCESS":
            result = task.result
            return TaskResultResponse(
                task_id=task_id,
                status="completed",
                result=SummarizeResponse(**result["result"])
                if result["status"] == "completed"
                else None,
                created_at=datetime.utcnow(),
                completed_at=datetime.fromisoformat(result["completed_at"]),
            )

        else:
            return TaskResultResponse(
                task_id=task_id,
                status="failed",
                error=str(task.info),
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task result: {str(e)}"
        )


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    redis_healthy = cache_service.health_check()
    return HealthCheck(
        status="healthy" if redis_healthy else "unhealthy",
        timestamp=datetime.utcnow(),
    )


@router.get("/stats")
async def get_stats():
    """Get basic service statistics from Redis."""
    try:
        redis_info = cache_service.redis_client.info()
        hits = redis_info.get("keyspace_hits", 0)
        misses = redis_info.get("keyspace_misses", 0)

        return {
            "redis_connected_clients": redis_info.get("connected_clients", 0),
            "redis_used_memory": redis_info.get("used_memory_human", "0B"),
            "redis_keyspace_hits": hits,
            "redis_keyspace_misses": misses,
            "cache_hit_ratio": round(hits / max(hits + misses, 1) * 100, 2),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )  