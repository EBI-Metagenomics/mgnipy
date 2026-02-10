from asyncio import Semaphore


def get_semaphore(concurrency: int = 5) -> Semaphore:
    return Semaphore(concurrency)
