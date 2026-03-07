import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.config import settings


class EvaluationService:

    LANG_MAP = {
        'en': ['english', 'en', 'eng', 'إنجليزي'],
        'fr': ['french', 'fr', 'français', 'فرنسي'],
        'es': ['spanish', 'es', 'español', 'إسباني'],
        'de': ['german', 'de', 'deutsch', 'ألماني'],
        'ar': ['arabic', 'ar', 'عربي']
    }

    def __init__(self, llm_model):
        self.llm_model = llm_model

    def detect_language(self, header: str) -> str:
        header_lower = header.lower()
        for lang_code, patterns in self.LANG_MAP.items():
            if any(pattern in header_lower for pattern in patterns):
                return lang_code
        return 'en'

    def _process_row(self, index, source_text, translated_text, source_lang, target_lang, total, get_justification):
        """Process a single row: evaluate, back-translate, and evaluate back-translation."""
        start_time = time.time()
        print(f"Starting row {index+1}/{total}...")
        
        # Add a small delay to avoid hitting Rate Limits
        if settings.API_REQUEST_DELAY > 0:
            time.sleep(settings.API_REQUEST_DELAY)

        if get_justification:
            score_translation, justification_translation = self.llm_model.evaluate_with_justification(
                source_text, translated_text, source_lang, target_lang
            )
        else:
            score_translation = self.llm_model.evaluate(
                source_text, translated_text, source_lang, target_lang
            )
            justification_translation = None

        back_translation = self.llm_model.translate(
            translated_text, target_lang, source_lang
        )

        duration = time.time() - start_time
        print(f"Finished row {index+1}/{total} ✅ (Took {duration:.2f}s)")
        return index, score_translation, justification_translation, back_translation

    def evaluate_excel_process(self, df: pd.DataFrame, get_justification: bool = True) -> pd.DataFrame:

        if len(df.columns) < 2:
            raise ValueError("Excel file must contain at least two columns.")

        source_column = df.columns[0]
        target_column = df.columns[1]

        source_lang = self.detect_language(source_column)
        target_lang = self.detect_language(target_column)

        df["score_translation"] = None
        df["justification_translation"] = None
        df["back_translation"] = None

        total = len(df)

        # Reduced max_workers to be more stable with API rate limits
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(
                    self._process_row,
                    index, row[source_column], row[target_column],
                    source_lang, target_lang, total, get_justification
                ): index
                for index, row in df.iterrows()
            }

            for future in as_completed(futures):
                try:
                    idx, score_t, just_t, back_t = future.result()
                    df.at[idx, "score_translation"] = score_t
                    df.at[idx, "justification_translation"] = just_t
                    df.at[idx, "back_translation"] = back_t
                except Exception as e:
                    print(f"Error processing row: {e}")

        if not get_justification:
            print("DEBUG: Dropping justification_translation column as requested.")
            df.drop(columns=["justification_translation"], inplace=True)

        print("Done! All rows processed.")
        return df
