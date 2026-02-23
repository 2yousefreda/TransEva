import re
from google import genai
from google.genai import types
from .LLMModel import LLMModel
from .llm_evaluator import LLMEvaluator


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

    def evaluate(self, original_text: str, translation: str, source_lang: str, target_lang: str) -> float:
        prompt = LLMEvaluator.get_evaluation_prompt(original_text, translation, target_lang)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )
            text_response = response.text.strip()
            return LLMEvaluator.parse_grade(text_response)
        except Exception as e:
            print(f"Error in evaluate: {e}")
            return 0.1

    def evaluate_with_justification(self, original_text: str, translation: str, source_lang: str, target_lang: str) -> tuple[float, str]:
        score = self.evaluate(original_text, translation, source_lang, target_lang)
        
        just_prompt = LLMEvaluator.get_justification_prompt(original_text, translation, target_lang, score)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=just_prompt,
                config=self.generation_config,
            )
            justification = response.text.strip()
            return score, justification
        except Exception as e:
            print(f"Error in get_justification: {e}")
            return score, ""

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
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
            return response.text.strip()
        except Exception as e:
            print(f"Error in translate: {e}")
            return ""
