import asyncio

CONCURRENCY_LIMIT = 5


def get_semaphore(concurrency: int = 5) -> asyncio.Semaphore:

    # Ensure that the concurrency does not exceed the defined limit
    _concurrency = min(concurrency, CONCURRENCY_LIMIT)

    return asyncio.Semaphore(_concurrency)
