from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, model: str, max_tokens: int = 1024) -> str:
        pass
