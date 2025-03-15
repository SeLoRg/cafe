from functools import wraps
from fastapi import HTTPException
from fastapi import HTTPException
from common.logger import logger


def exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            logger.error(f"{e}")
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logger.error(f"{e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred")

    return wrapper
