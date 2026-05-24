from enum import Enum

class ResponseSignal(Enum):
    
    FILE_VALIDATED_SUCCESS = "file_validated successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCEEDED = "processing_succeeded"
    NO_FILES_ERROR = "no_files_found"
    FILE_ID_ERROR = "no_file_found_with_this_id"
    PROJECT_NOT_FOUND_ERROR = "project_was_not_found"
    INSERT_INTO_VECTORDB_ERROR = " insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = " insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    VECTORDB_SEARCH_SUCCESS = "vectordb_search_success"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"
    LLM_CONFIGURATION_ERROR = "llm_configuration_error"
    LLM_QUOTA_EXCEEDED = "llm_quota_exceeded"
    LLM_SERVICE_UNAVAILABLE = "llm_service_unavailable"
