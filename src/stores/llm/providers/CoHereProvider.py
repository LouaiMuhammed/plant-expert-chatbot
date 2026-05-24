from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
from cohere.core.api_error import ApiError
from cohere.errors.not_found_error import NotFoundError
from cohere.errors.too_many_requests_error import TooManyRequestsError
from ..exceptions import LLMProviderError
from models import ResponseSignal

class CoHereProvider(LLMInterface):
    def __init__(self, api_key: str,
                 default_input_max_characters: int=1000,
                 default_output_max_characters: int=1000,
                 default_generation_temperature: float=0.1):
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums
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
            self.logger.error("CoHere client was not set")
            return None
    
        if not self.generation_model_id:
            self.logger.error("Generation model for Cohere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_characters
        temperature = temperature if temperature is not None else self.default_generation_temperature
        chat_history = list(chat_history or [])

        try:
            response = self.client.chat(
                model = self.generation_model_id,
                chat_history = chat_history,
                message = self.process_text(prompt),
                temperature = temperature,
                max_tokens = max_output_tokens
            )
        except NotFoundError as exc:
            self.logger.exception("Cohere model configuration error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_CONFIGURATION_ERROR.value,
                message=f"Cohere model '{self.generation_model_id}' is not available. Update GENERATION_MODEL_ID to a supported model.",
                status_code=500
            ) from exc
        except TooManyRequestsError as exc:
            self.logger.exception("Cohere quota or rate limit error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="Cohere quota exceeded or rate limited. Please retry later.",
                status_code=429
            ) from exc
        except ApiError as exc:
            self.logger.exception("Cohere API error while generating text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"Cohere request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        return response.text

    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type= CoHereEnums.QUERY.value

        try:
            response = self.client.embed(
                model = self.embedding_model_id,
                texts = [self.process_text(text)],
                input_type = input_type,
                embedding_types=['float']
            )
        except NotFoundError as exc:
            self.logger.exception("Cohere model configuration error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_CONFIGURATION_ERROR.value,
                message=f"Cohere model '{self.embedding_model_id}' is not available. Update EMBEDDING_MODEL_ID to a supported model.",
                status_code=500
            ) from exc
        except TooManyRequestsError as exc:
            self.logger.exception("Cohere quota or rate limit error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="Cohere quota exceeded or rate limited. Please retry later.",
                status_code=429
            ) from exc
        except ApiError as exc:
            self.logger.exception("Cohere API error while embedding text")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"Cohere request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding with CoHere")
            return None
        
        return response.embeddings.float[0]

    def embed_texts(self, texts: list, document_type: str = None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        try:
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=[self.process_text(text) for text in texts],
                input_type=input_type,
                embedding_types=['float']
            )
        except NotFoundError as exc:
            self.logger.exception("Cohere model configuration error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_CONFIGURATION_ERROR.value,
                message=f"Cohere model '{self.embedding_model_id}' is not available. Update EMBEDDING_MODEL_ID to a supported model.",
                status_code=500
            ) from exc
        except TooManyRequestsError as exc:
            self.logger.exception("Cohere quota or rate limit error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_QUOTA_EXCEEDED.value,
                message="Cohere quota exceeded or rate limited. Please retry later.",
                status_code=429
            ) from exc
        except ApiError as exc:
            self.logger.exception("Cohere API error while embedding batch")
            raise LLMProviderError(
                signal=ResponseSignal.LLM_SERVICE_UNAVAILABLE.value,
                message=f"Cohere request failed with status {exc.status_code}.",
                status_code=502
            ) from exc

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding batch with CoHere")
            return None

        return response.embeddings.float

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }
