import asyncio
import functools
from bigtree import Tree
from typing import Any, Optional, Literal
from mgnipy.V2.mgni_py_v2 import Client
from mgnipy.V2.mgni_py_v2.api.miscellaneous import list_mgnify_biomes
from mgnipy._shared_helpers.pydantic_help import int_gt_adapter
from mgnipy.V2.planning import planner, previewer
from mgnipy.V2 import BASE_URL
from mgnipy._shared_helpers.async_helpers import collect_pages

def retrieve_biome_pages():
    """Retrieves biomes and caches them for future use (since < 500)"""
    page_size = 50
    
    # init 
    client = Client(
        base_url=BASE_URL
    )

    # 
    plan_dict = planner(
        client=client,
        mgni_py_module=list_mgnify_biomes,
        page_size=page_size,
        max_depth=150
    )

    results = asyncio.run(
        collect_pages(
            client=client,
            mgni_py_module=list_mgnify_biomes, 
            total_pages=plan_dict['total_pages'], 
            page_size=page_size,
        )
    )

    return results
    
results = retrieve_biome_pages()



# class BiomeTree(Tree): 

#     def __init__(
#         self, 
#         *,
#         name: Optional[str] = None,
#         max_depth: Optional[int] = None,
#         page_size: int = 100, #max
#     ):
        

#         super().__init__(name, **kwargs)


    