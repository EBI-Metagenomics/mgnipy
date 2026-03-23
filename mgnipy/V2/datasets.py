import warnings
import webbrowser
from pathlib import Path
from typing import (
    Callable,
    Optional,
)

import httpx
import pandas as pd
from pydantic import (
    DirectoryPath,
    HttpUrl,
)

from mgnipy._models.config import MgnipyConfig
from mgnipy._shared_helpers.async_helpers import get_semaphore
from mgnipy.V2.mgni_py_v2 import Client
from mgnipy.V2.mgni_py_v2.models.m_gnify_analysis_with_annotations import (
    MGnifyAnalysisWithAnnotations,
)

# from mgnipy.V2.mgni_py_v2.api.analyses import (
#     analysis_get_mgnify_analysis_with_annotations_661c2d6a as get_analysis_annotations,
# )


semaphore = get_semaphore()
BASE_URL = MgnipyConfig().base_url


class MGazine(MGnifyAnalysisWithAnnotations):
    """More so an extended data class"""

    def __init__(self, **data):
        super().__init__(
            **data,
        )
        # self.mgnifier_helper = MGnifier(accession=self.accession)
        # self.mgnifier_helper.endpoint_module =
        # for client
        self._base_url: str = BASE_URL

    @property
    def downloads_dict(self) -> dict[str, dict]:
        # TODO
        return self.downloads

    @property
    def downloads_df(self) -> pd.DataFrame:
        return pd.DataFrame([x.to_dict() for x in self.downloads])

    @property
    def list_downloads_files(self):
        return {f.alias: f.url for f in self.downloads}

    def _get_url_by_alias(
        self, alias: str, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        df = df or self.downloads_df
        try:
            return df.query(f"alias == '{alias}'")["url"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting download url for alias: {alias}") from err

    def _get_alias_by_url(
        self, url: HttpUrl, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        df = df or self.downloads_df
        try:
            return df.query(f"url == '{url}'")["alias"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting alias for url: {url}") from err

    def _get_type_by_alias(
        self, alias: str, df: Optional[pd.DataFrame] = None
    ) -> Optional[str]:
        df = df or self.downloads_df
        try:
            return df.query(f"alias == '{alias}'")["file_type"].values[0]
        except RuntimeError as err:
            raise KeyError(f"Issue getting file type for alias: {alias}") from err

    def _prioritize_alias(
        self, alias: Optional[str], url: Optional[HttpUrl], required: bool = False
    ) -> tuple[str, HttpUrl]:
        if alias and url:
            warnings.warn(
                "Both `alias` and `url` provided, ignoring `url`.", stacklevel=2
            )
            url = self._get_url_by_alias(alias)
        elif alias and not url:
            url = self._get_url_by_alias(alias)
        elif url and not alias:
            alias = self._get_alias_by_url(url)

        if required and not alias and not url:
            raise ValueError("Either `alias` or `url` must be provided.")

        return alias, url

    def stream_tsv(
        self, url: str, sep: str = "\t", chunksize: int = 1000, **pd_kwargs
    ) -> pd.DataFrame:
        return pd.read_csv(
            url, iterator=True, sep=sep, chunksize=chunksize, **pd_kwargs
        )

    def stream_html(self, url: str, **web_kwargs):
        return webbrowser.open(url, **web_kwargs)

    def stream_txt(self, url: str, **kwargs):
        with httpx.stream("GET", url, **kwargs) as response:
            response.raise_for_status()
            yield from response.iter_text()

    def _get_streamer(
        self, alias: Optional[str] = None, url: Optional[HttpUrl] = None, **kwargs
    ):

        _alias, _url = self._prioritize_alias(alias, url, required=True)

        # return stream based on file type
        file_type = self._get_type_by_alias(_alias)
        if file_type == "tsv":
            return self.stream_tsv(_url, **kwargs)
        elif file_type == "csv":
            return self.stream_tsv(_url, sep=",", **kwargs)
        elif file_type == "html":
            return lambda: self.stream_html(_url, **kwargs)
        elif file_type in ["txt", "fasta", "fastq"]:
            return self.stream_txt(_url, **kwargs)
        else:
            raise ValueError(f"Unsupported file type for streaming: {file_type}")

    def stream(
        self, *, alias: Optional[str] = None, url: Optional[HttpUrl] = None
    ) -> dict[str, Callable]:
        """kinda lazy loading"""

        _alias, _url = self._prioritize_alias(alias, url)

        if not _alias and not _url:
            aliases = self.downloads_df["alias"].tolist()
        else:
            aliases = [_alias]

        return {a: self._get_streamer(alias=a) for a in aliases}

    def download(
        self,
        to_dir: DirectoryPath,
        alias: Optional[str] = None,
        *,
        url: Optional[str] = None,
        filename: Optional[str] = None,
    ):

        # get alias/url
        _alias, _url = self._prioritize_alias(alias, url, required=True)

        # make dir if not exists
        to_dir = Path(to_dir)
        to_dir.mkdir(parents=True, exist_ok=True)

        # prep full path
        filepath = to_dir / filename if filename else to_dir / _alias

        with httpx.stream("GET", _url) as response:
            response.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    def get(self, url: Optional[HttpUrl] = None, alias: Optional[str] = None):
        """here this will get all or a specific dataset"""
        with self._init_client() as client:
            # make get request
            response = client.get(url)
            # validate
            response.raise_for_status()
            # return content as bytes
            return response.content

    # def download(self, url: str, filename: str):
    #     with httpx.stream("GET", url) as response:
    #         response.raise_for_status()
    #         with open(filename, "wb") as f:
    #             for chunk in response.iter_bytes():
    #                 f.write(chunk)

    ## HIDDEN HELPER METHODS
    ## Help with requests
    def _init_client(self):
        """
        Initialize and return a MGnify API client instance.

        Returns
        -------
        Client
            Configured MGnify API client.
        """
        client_v1 = Client(
            base_url=str(self._base_url),
            # TODO logs?
        )
        return client_v1


# class DatasetBuilder(MGnifier):

#     def __init__(
#         self,
#         accession: str,
#     ):
#         super().__init__(
#             accession=accession,
#         )
#         self.mpy_module = get_analysis_annotations

#     def __getitem__(self, key):
#         pass

#     def __getattr__(seld, name):
#         if name == "annotations":
#             return self
#         else:
#             raise KeyError(f"DatasetBuilder object has no attribute {name}")

#     def export(self):
#         pass


# should there be different dataset builders?
# and they can be added to dataset builder as attributes?
