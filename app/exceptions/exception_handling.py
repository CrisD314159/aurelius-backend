from fastapi import HTTPException, status


class AureliusException(HTTPException):
    """Base Exception"""

    def __init__(self, status_code: int, detail: str, *,
                 success: bool = False, message: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.success = success
        self.message = message


class LLMNotLoadedException(AureliusException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            success=False,
            message="LLM not loaded",
            detail="LLM not loaded"
        )


class TTSException(AureliusException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class STTException(AureliusException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class TranscriptionException(AureliusException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class UnexpectedError(AureliusException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            message=detail,
            detail=detail
        )


class NotFoundException(AureliusException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            success=False,
            message=detail,
            detail=detail
        )
