# Tools for candidate CV parser and all "self" works

from src.providers.llm import LLMClient, LLMConfig
from dotenv import load_dotenv
import os

def check_resume(resume_text: str) -> str:
    llm = LLMClient()
    query = f"""
    Оцени резюме кандидата и выдели сильные и слабы стороны как ML специалиста. Не ошибайся, пожалуйста. Будь очень краток, буквально пара абзацев
    Резюме: {resume_text}
    """
    return llm.response(query)