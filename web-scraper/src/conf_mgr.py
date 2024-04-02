"""
This module implements and instantiates the common configuration class used in the project.
"""
# ───────────────────────────────────────────────────── imports ────────────────────────────────────────────────────── #

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                           specifies all modules that shall be loaded and imported into the                           #
#                                current namespace when we use 'from package import *'                                 #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #

__all__ = ["ConfManager", "conf_mgr"]


# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #
#                                                Configuration Manager                                                 #
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── #


class ConfManager:
    """Configuration Manager class"""

    path_src: Path = Path(__file__).parent.resolve()  # conf package
    path_project: Path = path_src.parent.resolve()  # project root
    path_data: Path = path_project.joinpath("data")  # data folder
    path_logs: Path = path_project.joinpath(".logs")  # logs folder
    path_logs.mkdir(parents=True, exist_ok=True)  # create the directory if it doesn't exist

    path_results: Path = path_project.joinpath("results")  # results folder
    path_results.mkdir(parents=True, exist_ok=True)  # create the directory if it doesn't exist

    # Configure the logger
    log_level = os.getenv("LOG_LEVEL", "INFO")  # Default to INFO if not set

    logger.remove()
    logger.add(sys.stderr, level=log_level)

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d-%H-%M-%S")

    log_file_name = path_logs / f"{timestamp}.log"
    logger.add(log_file_name, rotation="10 MB", level="DEBUG")


# --------------------------------------Instance----------------------------------------------------

conf_mgr: ConfManager = ConfManager()
