"""
Схемы данных для API.
"""
from .parcel import (
    ParcelTypeResponse,
    ParcelRegisterRequest,
    ParcelWebRegisterRequest,
    ParcelResponse
)
from .tasks import (
    PingRequest,
    TaskStatusResponse
)
from .common import (
    HTTPValidationError,
    ValidationError,
    SuccessResponse
)

__all__ = [
    # Parcel schemas
    'ParcelTypeResponse',
    'ParcelRegisterRequest',
    'ParcelWebRegisterRequest',
    'ParcelResponse',
    # Task schemas
    'PingRequest',
    'TaskStatusResponse',
    # Common schemas
    'HTTPValidationError',
    'ValidationError',
    'SuccessResponse',
]
