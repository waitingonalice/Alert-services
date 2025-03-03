from typing import Any


def Depends(func: Any) -> Any:
    """
    Non-native FastAPI Depends implementation.
    """
    if callable(func):
        return func()

    return func
