from __future__ import annotations

from asyncio import Semaphore

CONCURRENCY_LIMIT = 5


def get_semaphore(concurrency: int = 5) -> Semaphore:

    # Ensure that the concurrency does not exceed the defined limit
    _concurrency = min(concurrency, CONCURRENCY_LIMIT)

    return Semaphore(_concurrency)
