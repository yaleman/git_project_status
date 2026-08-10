#!/usr/bin/env python3


"""Scans the local directory for sub-directories that have
git repos in them, then does a git status on them"""

import os
from pathlib import Path
import sys
from typing import Optional

from git import Commit, Repo
from git.exc import GitCommandError

__version__ = "0.1.0"

if not os.environ.get("LOGURU_LEVEL"):
    os.environ["LOGURU_LEVEL"] = "INFO"

if os.environ.get("LOGURU_LEVEL") == "INFO":
    os.environ["LOGURU_FORMAT"] = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>"  # pylint: disable=line-too-long
    )

from loguru import logger  # pylint: disable=wrong-import-position


def handle_diff(
    repo_object: Repo,
    compare: Optional[Commit] = None,
    message: str = "Changes",
) -> None:
    """does the checking of the diffs, outputs information on what's changed"""
    try:
        diff = repo_object.head.commit.diff(other=compare)
    except ValueError as error_message:
        logger.error("Failed to get a diff in repo {} : {}", repo_object, error_message)
        return
    if diff:
        logger.info(f"{message}:")
        for diff_added in repo_object.head.commit.diff(other=compare):
            if diff_added.renamed_file:
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


def count_unpushed_commits(repo_object: Repo) -> Optional[int]:
    """Returns the number of local commits that are not yet pushed to upstream.

    Returns None when upstream state cannot be determined, for example when HEAD
    is detached or tracking isn't configured.
    """
    try:
        active_branch = repo_object.active_branch
    except TypeError as error_message:
        logger.debug(
            "{} has detached head, cannot compute upstream status: {}",
            repo_object.working_tree_dir,
            error_message,
        )
        return None

    tracking_branch_source = active_branch.tracking_branch
    if callable(tracking_branch_source):
        tracking_branch = tracking_branch_source()
    else:
        tracking_branch = tracking_branch_source
    if tracking_branch is None:
        return None

    try:
        return sum(
            1 for _ in repo_object.iter_commits(f"{tracking_branch}..{active_branch}")
        )
    except (GitCommandError, ValueError) as error_message:
        logger.debug(
            "Failed to compare commits for {}: {}",
            repo_object.working_tree_dir,
            error_message,
        )
        return None


def get_dir_to_check() -> Path:
    """figures out which directory we're trying to check"""
    if len(sys.argv) > 1:
        dir_to_check = Path(os.path.expanduser(sys.argv[1]))
        if not dir_to_check.exists():
            logger.error("Couldn't find specified directory: {}", dir_to_check)
            sys.exit(1)
    else:
        dir_to_check = Path("./")
    return dir_to_check
