import asyncio

import tqdm
from async_lru import alru_cache

from mgnipy import CACHE_DIR


def get_semaphore(concurrency: int = 5) -> asyncio.Semaphore:
    return asyncio.Semaphore(concurrency)


# def get_instance_attributes_str(obj):
#     cls = obj.__class__
#     # Try __dict__ first
#     if hasattr(obj, "__dict__"):
#         attrs = obj.__dict__
#     # Fallback to __slots__
#     elif hasattr(cls, "__slots__"):
#         slots = cls.__slots__
#         if isinstance(slots, str):
#             slots = [slots]
#         attrs = {slot: getattr(obj, slot) for slot in slots if hasattr(obj, slot)}
#     else:
#         attrs = {}
#     return f"{cls.__name__}({', '.join(f'{k}={v!r}' for k, v in attrs.items())})"


# def hasher(input) -> str:
#     if isinstance(input, dict):
#         hashable = ""
#         for key in input:
#             hashable += str(key) + str(input[key])
#         return hashable
#     elif isinstance(input, list):
#         hashable += "".join([str(i) for i in input])
#     elif isinstance(input, Callable):
#         hashable += input.__class__.__name__
#         hashable += get_instance_attributes_str(input)
#     else:
#         hashable += str(input)

#     return hashable


# def async_disk_lru_cache(cache_dir: Path = CACHE_DIR, maxsize: int = 32):
#     """
#     Decorator to cache async function results with both in-memory LRU and disk-based persistence.

#     This decorator combines an in-memory LRU cache with disk-based caching using pickle serialization.
#     Results are first checked in disk cache, then computed and stored if not found. The in-memory
#     LRU cache provides fast access to recently used results.

#     Parameters
#     ----------
#     cache_dir : Path, optional
#         Directory path where pickle files for disk cache will be stored.
#         Default is CACHE_DIR.
#     maxsize : int, optional
#         Maximum number of entries to keep in the in-memory LRU cache.
#         Default is 32.

#     Returns
#     -------
#     decorator : callable
#         A decorator function that wraps async functions to add caching behavior.

#     Notes
#     -----
#     - The cache key is generated from function arguments and keyword arguments.
#     - Hash collisions are possible but unlikely with standard Python hashing.
#     - Results must be pickle-serializable to use disk caching.
#     - The decorated function remains async and should be called with await.
#     - The cache_dir is created automatically if it does not exist.
#     """

#     # Decorator factory: takes cache directory and maxsize for in-memory cache
#     def decorator(func):
#         # In-memory async LRU cache
#         @alru_cache(maxsize=maxsize)
#         # Preserve original function metadata
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             # Create a unique key from args and kwargs
#             args = []
#             key = str({"args": args}) + str(kwargs)

#             # Generate a filename for disk cache using function name and key hash
#             fname = os.path.join(cache_dir, f"{func.__name__}_{hash(key)}.pkl")
#             # make directory if not exists
#             os.makedirs(cache_dir, exist_ok=True)

#             # if disk cache exists
#             if os.path.exists(fname):
#                 # load it
#                 with open(fname, "rb") as f:
#                     return pickle.load(f)
#             # else call the async function and cache result in memory and disk
#             result = await func(*args, **kwargs)
#             # disk cache
#             with open(fname, "wb") as f:
#                 pickle.dump(result, f)
#             return result

#         return wrapper

#     return decorator


# @async_disk_lru_cache()
# async def get_page(
#     client,
#     mgni_py_module,
#     page_num: int,
#     params: Optional[dict[str, Any]] = None,
#     concurrency: int = 5,
# ):
#     """coroutine function to get coroutine for each page"""
#     # limiting concurrency to protect server
#     async with get_semaphore(concurrency):
#         return await mgni_py_module.asyncio(
#             client=client,
#             **(params or {}),
#             page=page_num,
#         )


# async def collect_pages(
#     *,
#     client,
#     mgni_py_module,
#     total_pages: int,
#     pages: Optional[list[int]] = None,
#     params: Optional[dict[str, Any]] = None,
# ) -> list[dict]:

#     if isinstance(pages, list):
#         if not all(p <= total_pages for p in pages):
#             raise ValueError(
#                 f"One or more specified pages exceed total pages {total_pages}."
#                 f"Specified pages: {pages}"
#             )
#     elif pages is None:
#         pages = list(range(1, total_pages + 1))
#     else:
#         raise ValueError("pages must be a list of integers or None")

#     # creating async tasks
#     async_tasks = [
#         asyncio.create_task(get_page(client, mgni_py_module, page_num, params))
#         for page_num in pages
#     ]

#     results = []
#     # gathering results as completed
#     for task in tqdm(asyncio.as_completed(async_tasks), total=len(async_tasks)):
#         page_result = await task
#         results.append(page_result.to_dict())

#     return results
