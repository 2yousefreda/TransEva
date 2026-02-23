from abc import ABC, abstractmethod

class LLMModel(ABC):
    @abstractmethod
    def evaluate(self, source: str, translation: str) -> float:
        pass

    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        pass

