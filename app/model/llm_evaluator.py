import logging
import re
from google import genai
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMEvaluator:
    """Evaluates translation quality using Gemini LLM as judge"""
    
    # Grade to score mapping (A=1.0, B=0.9, ..., J=0.1)
    GRADE_TO_SCORE = {
        'A': 1.00,
        'B': 0.90,
        'C': 0.80,
        'D': 0.70,
        'E': 0.60,
        'F': 0.50,
        'G': 0.40,
        'H': 0.30,
        'I': 0.20,
        'J': 0.10
    }
    
    EVALUATION_PROMPT = """
You are an expert linguist and theologian specializing in Arabic-to-{target_language} translations of Islamic literature. Your task is to evaluate a translation based on linguistic accuracy, theological precision, and cultural preservation.

### Evaluation Criteria

1. **Theological Accuracy (Aqidah & Fiqh)**:
   - Does the translation preserve the doctrinal meaning?
   - Are Divine Names and Attributes handled with appropriate reverence and capitalization?
   - Are technical terms (e.g., 'Taqwa', 'Ihsan') either translated accurately or transliterated with clear context?

2. **Linguistic Fidelity**:
   - Does the {target_language} capture the rhetorical weight (Balagha) of the Arabic source?
   - Is the tone appropriate for religious discourse (dignified, not overly colloquial)?

3. **Fluency**:
   - Is the {target_language} grammatically correct and natural to a native reader, without sounding awkward or "translationese"?

4. **Language Purity & Transliteration Rules** (CRITICAL):
   - The translation MUST be entirely in {target_language}.
   - **Transliteration of standard Islamic terms and liturgical phrases IS ACCEPTABLE** (e.g., "Allah", "Salah", "Shahada", Adhan phrases).
   - **For ritual phrases (like the Adhan or Shahada):** Pure transliteration (e.g., "Allahu Akbar", "La ilaha illallah") is considered a **PERFECT translation (Grade A)** if it follows the standard spelling in {target_language} Islamic literature. Do NOT penalize for lack of semantic translation in these specific ritual contexts.
   - **Mixed language usage is NOT acceptable**: Code-switching (untranslated Arabic sentences mixed with {target_language}) is a failure, EXCEPT for the specific ritual phrases mentioned above.

5. **Citations & References**:
   - If the source text is purely a citation (e.g., "[Al-Baqara: 255]"), the translation MUST be the corresponding citation in {target_language}.
   - **Do NOT penalize** for not including the full verse text if it was not in the source.
   - **Transliteration Variations**: Minor variations in Surah name transliteration are acceptable and should NOT be penalized if the Surah is clearly identifiable.

### Grading Scale (A-J)
- **A (Exceptional)**: Flawless. Captures nuance, theology, and tone perfectly. Includes accurate standard transliteration of ritual phrases.
- **B (Excellent)**: Strong translation. Minor stylistic choices that do not affect meaning.
- **C (Very Good)**: Accurate meaning. Occasional stiffness in {target_language} phrasing.
- **D (Good)**: Generally accurate. Minor loss of nuance or slight awkwardness.
- **E (Acceptable)**: Meaning is preserved, but phrasing is clunky or lacks reverence.
- **F (Mediocre)**: Noticeable errors in grammar, significant loss of rhetorical style, OR mixed language usage.
- **G (Poor)**: Minor theological ambiguities or distracting grammatical issues.
- **H (Very Poor)**: Significant meaning distortion or inappropriate vocabulary.
- **I (Severely Flawed)**: Theologically misleading or grammatically broken.
- **J (Failed)**: Unintelligible or completely inaccurate.

### Input
**Source Text (Arabic):**
{source}

**Target Text ({target_language}):**
{translation}

### Output Instructions
{output_format_instructions}
"""

    @classmethod
    def get_evaluation_prompt(cls, source: str, translation: str, target_language: str, include_reason: bool = False) -> str:
        output_format_instructions = cls._build_output_format_instructions(include_reason)
        return cls.EVALUATION_PROMPT.format(
            source=source,
            translation=translation,
            target_language=target_language,
            output_format_instructions=output_format_instructions
        )

    @staticmethod
    def _build_output_format_instructions(include_reason: bool) -> str:
        if include_reason:
            return (
                "Respond with EXACTLY two lines and no extra text:\n"
                "GRADE: <A-J>\n"
                "REASON: <ONE concise Arabic sentence justifying the grade>\n"
                "Do not output markdown, bullet points, or additional commentary."
            )
        return (
            "Respond with EXACTLY one line and no extra text:\n"
            "GRADE: <A-J>\n"
            "Do not include any explanation, reasoning, or additional text."
        )

    @classmethod
    def parse_response(cls, raw_response: str, include_reason: bool = False) -> tuple[float, str | None]:
        if not raw_response:
            return 0.10, None

        grade_match = re.search(r"GRADE\s*[:\-]\s*([A-J])\b", raw_response, flags=re.IGNORECASE)
        grade = grade_match.group(1).upper() if grade_match else None
        
        if not grade:
            # Fallback to looking for A-J anywhere if the structured format failed
            for char in raw_response.strip().upper():
                if char in 'ABCDEFGHIJ':
                    grade = char
                    break
        
        score = cls.GRADE_TO_SCORE.get(grade, 0.10)
        
        justification = None
        if include_reason:
            reason_match = re.search(r"REASON\s*[:\-]\s*(.+)", raw_response, flags=re.IGNORECASE | re.DOTALL)
            if reason_match:
                justification = reason_match.group(1).strip()
                
        return score, justification
