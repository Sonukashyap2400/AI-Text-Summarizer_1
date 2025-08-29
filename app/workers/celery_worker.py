from celery import Celery
from datetime import datetime
import asyncio
import json

from app.config import settings
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service
from app.models import SummaryType


# Initialize Celery
celery_app = Celery(
    "summarizer_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,   # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True)
def summarize_text_task(self, text: str, summary_type: str, max_words: int = None):
    """Background task for text summarization."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Update task status
        self.update_state(
            state="PROCESSING",
            meta={"status": "Processing text summarization"}
        )

        # Check cache first
        cached_result = loop.run_until_complete(
            cache_service.get(text, summary_type, max_words)
        )
        if cached_result:
            return {
                "status": "completed",
                "result": cached_result,
                "from_cache": True,
                "completed_at": datetime.utcnow().isoformat(),
            }

        # Generate new summary
        summary_type_enum = SummaryType(summary_type)
        result = loop.run_until_complete(
            ai_service.summarize_text(text, summary_type_enum, max_words)
        )

        # Cache the result
        result_dict = result.dict()
        loop.run_until_complete(
            cache_service.set(text, summary_type, result_dict, max_words)
        )

        return {
            "status": "completed",
            "result": result_dict,
            "from_cache": False,
            "completed_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat(),
        }

    finally:
        loop.close()  