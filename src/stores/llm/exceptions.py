class LLMProviderError(Exception):
    def __init__(self, signal: str, message: str, status_code: int = 503):
        super().__init__(message)
        self.signal = signal
        self.message = message
        self.status_code = status_code
