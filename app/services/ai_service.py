import google.generativeai as genai
from app.config import settings
from app.models import SummaryType, SummarizeResponse
import time
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def _build_prompt(self, text: str, summary_type: SummaryType, max_words: int = None) -> str:
        base_prompt = f"Please summarize the following text:\n\n{text}\n\n"

        if summary_type == SummaryType.BRIEF:
            prompt = base_prompt + "Provide a brief, concise summary that captures the main points."
        elif summary_type == SummaryType.DETAILED:
            prompt = base_prompt + "Provide a detailed summary that covers all important aspects and key details."
        elif summary_type == SummaryType.BULLET_POINTS:
            prompt = base_prompt + "Provide a summary in bullet points format, highlighting key points clearly."

        if max_words:
            prompt += f" Keep the summary under {max_words} words."

        return prompt

    async def summarize_text(self, text: str, summary_type: SummaryType, max_words: int = None) -> SummarizeResponse:
        start_time = time.time()
        try:
            prompt = self._build_prompt(text, summary_type, max_words)

            response = self.model.generate_content(prompt)

            summary = response.text.strip()
            processing_time = time.time() - start_time

            original_length = len(text.split())
            summary_length = len(summary.split())
            compression_ratio = round((original_length - summary_length) / original_length * 100, 2)

            return SummarizeResponse(
                summary=summary,
                original_length=original_length,
                summary_length=summary_length,
                compression_ratio=compression_ratio,
                processing_time=round(processing_time, 2)
            )

        except Exception as e:
            logger.error(f"Gemini summarization failed: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}")

# Global instance
ai_service = AIService() 