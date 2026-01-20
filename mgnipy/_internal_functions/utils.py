# these functions are pretty general (file that can be reused across projects)
import argparse
import glob
import os
import sys
from datetime import datetime
from logging import DEBUG, FileHandler, Formatter, Logger, StreamHandler
from pathlib import Path
from typing import Optional

import yaml
from pydantic import (
    TypeAdapter,
    DirectoryPath, 
    FilePath, 
    StrictBool, 
    validate_call
)

fpath_adapter = TypeAdapter(FilePath)
bool_adapter = TypeAdapter(StrictBool)


def create_folder(directory_path: Path, is_nested: bool = False):
    """
    Creates a folder if it doesn't exist.

    Parameters
    ----------
    - directory_path (Path): path to the folder to create
    - is_nested (bool): whether to create nested folders

    Returns
    -------
    None
        prints status message

    Examples
    --------
    >>> create_folder('data/logs', is_nested=True) # doctest: +SKIP
    Created nested directory 'data/logs'
    >>> # if you run it again it will say it already exists
    >>> create_folder('data/logs', is_nested=True) # doctest: +SKIP
    Folder 'data/logs' already exists.
    """
    # checks is a str or path
    path = Path(directory_path)

    # make sure it is not an existing file
    if path.is_file():
        raise ValueError(
            "directory_path is an existing file."
            f"should be a folder/foldername: {directory_path}"
        )
    # if folder already exists
    elif path.is_dir():
        # do nothing
        print(f"Folder '{directory_path}' already exists.")
    # create the folder(s)
    else:
        try:
            if is_nested:
                # Create the directory and any necessary parent directories
                os.makedirs(directory_path, exist_ok=True)
                print(f"Created nested directory '{directory_path}'")
            else:
                # Create only the final directory (not nested)
                os.mkdir(directory_path)
                print(f"Created directory '{directory_path}'")
        except OSError as e:
            raise OSError(f"Error creating directory '{directory_path}': {e}")


# FUNCTIONS FOR CONFIG
def config_loader(filepath: FilePath) -> dict:
    """
    Loads a YAML config file as a dictionary.

    Parameters
    ----------
    filepath : FilePath
        Path to the config file.

    Returns
    -------
    dict
        Configuration parameters as a dictionary.

    Examples
    --------
    >>> config_dict = config_loader('config/config.yaml') # doctest: +SKIP
    """

    fpath_adapter.validate_python(filepath)

    with open(filepath, "r") as f:
        contents = yaml.safe_load(f)

    # post check
    assert isinstance(contents, dict), "content not returned as a dict"

    return contents


def get_args(prog_name: str, **kwargs) -> argparse.Namespace:
    """
    Initiates argparse.ArgumentParser() and adds common arguments.

    Parameters
    ----------
    prog_name : str
        The name of the program.
    **kwargs : dict
        Additional keyword arguments for ArgumentParser.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    # init
    parser = argparse.ArgumentParser(prog=prog_name, **kwargs)
    # config file path
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        default="docs/tutorial/some-demo-config.yaml",
        help="provide path to config yaml file",
    )

    args = parser.parse_args()
    return args


@validate_call
def get_basename(fname: Optional[FilePath] = None) -> str:
    """
    Returns the base filename without extension.

    If `fname` is provided, returns the basename (without extension) of the given file path.
    If `fname` is None, returns the basename (without extension) of the script being executed.

    Parameters
    ----------
    fname : FilePath or None, optional
        The file path to extract the basename from. If None, uses the current script's filename.

    Returns
    -------
    str
        Basename of the given file path or the current script, without file extension.

    Examples
    --------
    >>> get_basename()
    'utils'
    >>> get_basename('this/is-a-filepath.csv')
    'is-a-filepath'
    """

    if fname is None:
        return os.path.splitext(os.path.basename(sys.argv[0]))[0]
    else:
        return os.path.splitext(os.path.basename(fname))[0]


def get_time(incl_time: StrictBool = True, incl_timezone: StrictBool = True) -> str:
    """
    Gets current date, time (optional), and timezone (optional) for file naming.

    Parameters
    ----------
    incl_time : StrictBool, optional
        Whether to include timestamp in the string. Default is True.
    incl_timezone : StrictBool, optional
        Whether to include the timezone in the string. Default is True.

    Returns
    -------
    fname : str
        String including date, timestamp and/or timezone, connected by '_' (e.g., 'yyyyMMdd_hhmm_timezone').

    Examples
    --------
    >>> get_time()  # doctest: +SKIP
    '20231019_101758_CEST'
    >>> get_time(incl_time=False)  # doctest: +SKIP
    '20231019_CEST'
    """
    # validate inputs
    bool_adapter.validate_python(incl_time)
    bool_adapter.validate_python(incl_timezone)

    # getting current time and timezone
    the_time = datetime.now()
    timezone = datetime.now().astimezone().tzname()
    # convert date parts to string
    y = str(the_time.year)
    M = str(the_time.month)
    d = str(the_time.day)
    h = str(the_time.hour)
    m = str(the_time.minute)
    s = str(the_time.second)
    # putting date parts into one string
    if incl_time and incl_timezone:
        fname = "_".join([y + M + d, h + m + s, timezone])
    elif incl_time:
        fname = "_".join([y + M + d, h + m + s])
    elif incl_timezone:
        fname = "_".join([y + M + d, timezone])
    else:
        fname = y + M + d
    # post checks
    parts = fname.split("_")
    if incl_time and incl_timezone:
        assert len(parts) == 3, f"time and/or timezone inclusion issue: {fname}"
    elif incl_time or incl_timezone:
        assert len(parts) == 2, f"time/timezone inclusion issue: {fname}"
    else:
        assert len(parts) == 1, f"time/timezone inclusion issue: {fname}"
    return fname


class AutoLogger(Logger):
    """
    AutoLogger extends the standard Logger to automatically handle log file creation and optional stdout logging.

    Parameters
    ----------
    name : str, optional
        Name for the logger. If None, uses the basename of the current script.
    output_folder : Path, optional
        Directory where log files will be stored. Default is "logs".
    stdout : bool, optional
        If True, log messages are also output to stdout. Default is True.
    msg_format : str, optional
        Format string for log messages. Default is "[%(asctime)s] %(name)s: %(levelname)s - %(message)s".
    """

    def __init__(
        self,
        name: Optional[str] = None,
        output_folder: Path = "logs",
        stdout: bool = True,
        msg_format: str = "[%(asctime)s] %(name)s: %(levelname)s - %(message)s",
    ):
        """
        Initialize the AutoLogger.

        Parameters
        ----------
        name : str, optional
            Name for the logger. If None, uses the basename of the current script.
        output_folder : Path, optional
            Directory where log files will be stored. Default is "logs".
        stdout : bool, optional
            If True, log messages are also output to stdout. Default is True.
        msg_format : str, optional
            Format string for log messages. Default is "[%(asctime)s] %(name)s: %(levelname)s - %(message)s".
        """
        # assign attr
        self.output_folder = output_folder
        self.msg_format = msg_format
        self.stdout = stdout
        self.name = name or get_basename()
        super().__init__(name)
        # create folder if not exists
        create_folder(output_folder)
        # create filename
        self.filename = self._create_filename(suffix=self.name)
        self._setup_handlers()
        self.setLevel(DEBUG)

    # hidden methods
    def _create_filename(self, suffix: str) -> str:
        """
        Create log file name and path.

        Parameters
        ----------
        suffix : str
            Additional string to append to the log file name.

        Returns
        -------
        str
            The file path to the log file.
        """
        log_filename = get_time(incl_timezone=False) + "_" + suffix + ".log"
        self.filename = os.path.join(self.output_folder, log_filename)
        return self.filename

    def _setup_handlers(self):
        """
        Set up logging handlers for file and optional stdout.

        Returns
        -------
        None
        """
        # init handlers
        self.handlers = [FileHandler(filename=self.filename)]
        if self.stdout:
            self.handlers.append(StreamHandler(stream=sys.stdout))
        # then format
        for handler in self.handlers:
            handler.setFormatter(Formatter(self.msg_format))
            # and assign handlers
            self.addHandler(handler)


@validate_call
def filter_filepaths(
    fpath: DirectoryPath | list[FilePath],
    identifiers: list[str] = [""],
    exclude: Optional[list[str]] = None,
) -> list:
    """
    Isolating files to iterate through. Can provide multiple identifiers.
    if list given, then filters list.
    if str/path given, then acquires list first.
    """

    # if path (str) given then get a list of files first
    if type(fpath) is DirectoryPath:
        # get list of containing files
        filepaths = glob.glob(f"{fpath}/**", recursive=True)
    # if a list of filenames then continue
    elif type(fpath) is list:
        filepaths = fpath
    else:
        raise TypeError(f"fpath must be a string or list: {type(fpath)}")

    # filtering for files that have those identifiers
    in_filtered = [
        file
        for file in filepaths
        if all([id in os.path.basename(file) for id in identifiers])
    ]

    if exclude is None:
        return in_filtered
    else:
        # filter out the files that match in the exclusion list
        ex_filtered = [
            file
            for file in in_filtered
            if all([ex not in os.path.basename(file) for ex in exclude])
        ]
        return ex_filtered
