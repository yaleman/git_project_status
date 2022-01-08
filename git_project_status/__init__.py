#!/usr/bin/env python3


""" Scans the local directory for sub-directories that have
git repos in them, then does a git status on them """

import os
from pathlib import Path
import sys
from git import Repo  # type: ignore
from git.exc import InvalidGitRepositoryError  # type: ignore

__version__ = "0.0.11"

if not os.environ.get("LOGURU_LEVEL"):
    os.environ["LOGURU_LEVEL"] = "INFO"

if os.environ.get("LOGURU_LEVEL") == "INFO":
    os.environ[
        "LOGURU_FORMAT"
    ] = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"  # pylint: disable=line-too-long

from loguru import logger  # pylint: disable=wrong-import-position


def handle_diff(repo_object, compare=None, message="Changes"):
    """ does the checking of the diffs """
    if repo_object.head.commit.diff(compare):
        logger.info(f"{message}:")
        for diff_added in repo_object.head.commit.diff(compare):
            if diff_added.renamed:
                logger.info(
                    "renamed : {} -> {}", diff_added.rename_from, diff_added.rename_to
                )
            elif diff_added.new_file:
                logger.info("new file: {}", diff_added.b_path)
            elif diff_added.change_type == "M":
                logger.info("modified: {}", diff_added.b_path)
            elif diff_added.change_type == "D":
                logger.info("deleted:  {}", diff_added.b_path)
            else:
                logger.error("Unknown change type: '{}'", diff_added.change_type)
                logger.error(diff_added)
                logger.debug(dir(diff_added))


def get_dir_to_check() -> Path:
    """ figures out which directory we're trying to check """
    if len(sys.argv) > 1:
        dir_to_check = Path(os.path.expanduser(sys.argv[1]))
        if not dir_to_check.exists():
            logger.error("Couldn't find specified directory: {}", dir_to_check)
            sys.exit(1)
    else:
        dir_to_check = Path("./")
    return dir_to_check


def cli():
    """ does the thing... """
    dir_to_check = get_dir_to_check()
    found_repo = False
    logger.debug("Checking {}", dir_to_check)

    for filename in os.listdir(dir_to_check):
        dirpath = os.path.normpath(f"{dir_to_check}/{filename}")
        if os.path.isdir(dirpath):
            logger.debug(f"Found dir: {dirpath}")
            try:
                repo = Repo(dirpath)
            except InvalidGitRepositoryError as error_message:
                logger.debug(
                    "{} is not a repository, skipping ({})",
                    dirpath,
                    error_message,
                )
                continue
            if repo.bare:
                logger.info("{} is bare, ignoring.", dirpath)
                continue
            found_repo = True

            if repo.is_dirty():
                try:
                    logger.warning(
                        "{} ({}) dirty",
                        dirpath,
                        repo.active_branch,
                    )
                except TypeError as error_message:
                    if repo.head.is_detached:
                        logger.info(
                            "{} is detached from {}, can't process.",
                            dirpath,
                            repo.head.object,
                        )
                        continue
                    logger.error(
                        "dirpath({}) error: {}",
                        dirpath,
                        error_message,
                    )
                    continue
                if repo.untracked_files:
                    logger.info("Untracked files:")
                    for untracked_files in repo.untracked_files:
                        logger.info(f" {untracked_files}")
                handle_diff(
                    repo,
                    compare="HEAD",
                    message="Changes staged for commit",
                )
                handle_diff(
                    repo,
                    compare=None,
                    message="Changes not staged for commit",
                )

                logger.info("")
    if not found_repo:
        logger.warning("No repositories analysed.")
