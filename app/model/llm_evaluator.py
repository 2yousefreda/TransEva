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
Respond with ONLY a single letter (A, B, C, D, E, F, G, H, I, or J).
Do not include any explanation, reasoning, or additional text.
Just the letter grade.
"""

    JUSTIFICATION_PROMPT = """
You are an expert linguist reviewing Arabic-to-{target_language} translations of Islamic literature.
You are given the original Arabic text, the translation, and the numeric score previously assigned.

Write ONE concise Arabic sentence justifying the score.
- Be direct and specific.
- Do not use filler words or introductory phrases (e.g., "The score is low because...", "Based on the text...").
- Focus immediately on the error or quality.
- Do not output English.

### Input
**Source Text (Arabic):**
{source}

**Target Text ({target_language}):**
{translation}

**Assigned Score (0.10 to 1.00):**
{score:.2f}
"""

    @classmethod
    def get_evaluation_prompt(cls, source: str, translation: str, target_language: str) -> str:
        return cls.EVALUATION_PROMPT.format(
            source=source,
            translation=translation,
            target_language=target_language
        )

    @classmethod
    def get_justification_prompt(cls, source: str, translation: str, target_language: str, score: float) -> str:
        return cls.JUSTIFICATION_PROMPT.format(
            source=source,
            translation=translation,
            target_language=target_language,
            score=score
        )

    @classmethod
    def parse_grade(cls, grade_text: str) -> float:
        grade = grade_text.strip().upper()
        if grade in cls.GRADE_TO_SCORE:
            return cls.GRADE_TO_SCORE[grade]
        return 0.10
