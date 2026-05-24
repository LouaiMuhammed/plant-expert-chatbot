from ..LLMInterface import LLMInterface
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI, RateLimitError
import logging
from ..LLMEnums import OpenAIEnums
from ..exceptions import LLMProviderError
from models import ResponseSignal

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_characters: int=1000,
                 default_output_max_characters: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        client_kwargs = {"api_key": self.api_key}
        if self.api_url:
            client_kwargs["base_url"] = self.api_url

        self.client = OpenAI(**client_kwargs)

        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=None, max_output_tokens: int=None,
                    temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI model was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_characters
        temperature = temperature if temperature is not None else self.default_generation_temperature

        chat_history = list(chat_history or [])
        
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )

        try:
            response = self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
        except RateLimitError as exc:
            self.logger.exception("OpenAI quota or rate limit error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="OpenAI quota exceeded or rate limited. Check billing details and retry later.",
                status_code=429
            ) from exc
        except (APIConnectionError, APITimeoutError) as exc:
            self.logger.exception("OpenAI connection error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message="Unable to reach the OpenAI service right now. Please try again later.",
                status_code=503
            ) from exc
        except APIStatusError as exc:
            self.logger.exception("OpenAI API status error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"OpenAI request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        
        return response.choices[0].message.content

    def embed_text(self, text: str, document: str = None):
        if not self.client:
            self.logger.error("OpenAI model was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id,
                input=text
            )
        except RateLimitError as exc:
            self.logger.exception("OpenAI quota or rate limit error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="OpenAI quota exceeded or rate limited. Check billing details and retry later.",
                status_code=429
            ) from exc
        except (APIConnectionError, APITimeoutError) as exc:
            self.logger.exception("OpenAI connection error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message="Unable to reach the OpenAI service right now. Please try again later.",
                status_code=503
            ) from exc
        except APIStatusError as exc:
            self.logger.exception("OpenAI API status error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"OpenAI request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.data or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        return response.data[0].embedding

    def embed_texts(self, texts: list, document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI model was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id,
                input=texts
            )
        except RateLimitError as exc:
            self.logger.exception("OpenAI quota or rate limit error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="OpenAI quota exceeded or rate limited. Check billing details and retry later.",
                status_code=429
            ) from exc
        except (APIConnectionError, APITimeoutError) as exc:
            self.logger.exception("OpenAI connection error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message="Unable to reach the OpenAI service right now. Please try again later.",
                status_code=503
            ) from exc
        except APIStatusError as exc:
            self.logger.exception("OpenAI API status error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"OpenAI request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.data:
            self.logger.error("Error while embedding batch with OpenAI")
            return None

        return [item.embedding for item in response.data]
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
