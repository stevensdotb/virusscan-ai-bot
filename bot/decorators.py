from functools import wraps

def retry_on_reached_limit(http_exception, exception_handler=None, *, retries: int = 3, delay: int = 5):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                for _ in range(retries):
                    return await func(*args, **kwargs)
            except http_exception as e:
                if exception_handler is not None:
                    await exception_handler(e, delay)
                raise
        return wrapper
    return decorator