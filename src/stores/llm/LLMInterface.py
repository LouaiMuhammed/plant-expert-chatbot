from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str):
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                      temperature: float = None):
        
        pass

    @abstractmethod
    def embed_text(self, text: str, document: str = None):
        pass

    def embed_texts(self, texts: list, document_type: str = None):
        return [
            self.embed_text(text=text, document=document_type)
            for text in texts
        ]

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass

