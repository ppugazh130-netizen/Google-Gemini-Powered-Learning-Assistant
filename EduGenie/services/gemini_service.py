import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiServiceError(Exception):
    pass

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.client = None

        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise GeminiServiceError("GEMINI_API_KEY is missing in .env")

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as error:
            raise GeminiServiceError(f"Gemini initialization failed: {error}")

    def is_configured(self):
        return self.client is not None and bool(self.api_key)

    def ask(self, question, history=None):
        if not self.is_configured():
            raise GeminiServiceError("Gemini API key is not configured.")

        prompt = """You are EduGenie, an AI learning assistant for college students.
Give accurate, simple and exam-friendly answers.
Use clear headings, bullet points and examples when useful.
For programming questions, provide working code and a simple explanation.
For 2-mark questions, be short and direct.
For 10/16-mark questions, give a detailed, organized answer.
Do not make answers unnecessarily complicated.
"""

        if history:
            prompt += "\nPrevious conversation:\n"
            for item in history:
                if isinstance(item, dict):
                    role = item.get("role", "")
                    content = str(item.get("content", ""))
                    if role == "user":
                        prompt += f"Student: {content}\n"
                    elif role == "assistant":
                        prompt += f"EduGenie: {content}\n"

        prompt += f"\nStudent's question:\n{question}\n\nAnswer helpfully."

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            answer = getattr(response, "text", None)
            if not answer:
                raise GeminiServiceError("Gemini returned an empty response.")
            return answer.strip()
        except GeminiServiceError:
            raise
        except Exception as error:
            raise GeminiServiceError(f"Gemini API error: {error}")
