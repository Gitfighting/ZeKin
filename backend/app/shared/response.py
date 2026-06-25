from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: T
    message: str = "ok"


def success_response(data: T, message: str = "ok") -> ApiResponse[T]:
    return ApiResponse[T](data=data, message=message)
