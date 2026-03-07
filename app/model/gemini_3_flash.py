import time
from google import genai
from google.genai import types
from .LLMModel import LLMModel
from .llm_evaluator import LLMEvaluator
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import logging

logger = logging.getLogger(__name__)


class Gemini3Flash(LLMModel):
    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview"):
        if not api_key:
            raise RuntimeError("API_KEY is missing")

        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        self.generation_config = types.GenerateContentConfig(
            temperature=0.3,
            top_p=0.9,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def evaluate(self, original_text: str, translation: str, source_lang: str, target_lang: str) -> float:
        start = time.time()
        prompt = LLMEvaluator.get_evaluation_prompt(original_text, translation, target_lang, include_reason=False)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )
            score, _ = LLMEvaluator.parse_response(response.text, include_reason=False)
            print(f"  [Gemini] evaluate took {time.time()-start:.2f}s")
            return score
        except Exception as e:
            print(f"Error in evaluate (Row context unknown): {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def evaluate_with_justification(self, original_text: str, translation: str, source_lang: str, target_lang: str) -> tuple[float, str]:
        start = time.time()
        prompt = LLMEvaluator.get_evaluation_prompt(original_text, translation, target_lang, include_reason=True)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )
            score, justification = LLMEvaluator.parse_response(response.text, include_reason=True)
            print(f"  [Gemini] evaluate_with_justification took {time.time()-start:.2f}s")
            return score, justification or ""
        except Exception as e:
            print(f"Error in evaluate_with_justification (Row context unknown): {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        reraise=True
    )
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        start = time.time()
        prompt = (
            f"You are a strict translation engine. Your task is to translate the following text from {source_lang} to {target_lang}.\n"
            "CRITICAL RULES:\n"
            "1. Output ONLY the translated text.\n"
            "2. DO NOT include any introductory or concluding remarks (e.g., 'Here is the translation', 'Sure').\n"
            "3. DO NOT add any notes or explanations.\n"
            "4. Maintain the original tone and formatting exactly.\n"
            "5. If the text is already in the target language, return it exactly as is.\n"
            "6. DO NOT change or fix any grammatical errors or incoherence - translate exactly as written.\n\n"
            f"Input Text:\n{text}"
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )
            print(f"  [Gemini] translate took {time.time()-start:.2f}s")
            return response.text.strip()
        except Exception as e:
            print(f"Error in translate: {str(e)}")
            return ""
