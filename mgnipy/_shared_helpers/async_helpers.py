import asyncio


def get_semaphore(concurrency: int = 5) -> asyncio.Semaphore:
    return asyncio.Semaphore(concurrency)
