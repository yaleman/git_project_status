"""cli interface"""

import os
import sys
from loguru import logger

import click
from git import Repo
from git.exc import InvalidGitRepositoryError

from . import handle_diff


def process_paths(path: str, short: bool) -> None:
    """actually does the thing, split it out into its own function for testing"""
    found_repo = False
    logger.debug("Checking {}", path)

    for filename in os.listdir(path):
        dirpath = os.path.normpath(f"{path}/{filename}")
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
            except AttributeError as error_message:
                logger.error(
                    "{} AttributeError, skipping ({})",
                    dirpath,
                    error_message,
                )
                continue
            if repo.bare:
                logger.debug("{} is bare, ignoring.", dirpath)
                continue
            found_repo = True

            if repo.is_dirty():
                try:
                    logger.warning(
                        "{} ({})",
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
                if repo.untracked_files and not short:
                    logger.info("Untracked files:")
                    for untracked_files in repo.untracked_files:
                        logger.info(f" {untracked_files}")
                if not short:
                    handle_diff(
                        repo,
                        compare=None,
                        message="Changes not staged for commit",
                    )

                    logger.info("")
    if not found_repo:
        logger.warning("No repositories analysed.")


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("-s", "--short", is_flag=True, help="Show short status")
@click.option("-d", "--debug", is_flag=True, help="Show debug output")
def cli(path: str, short: bool, debug: bool) -> None:
    """Checks for dirty repositories in sub-directories and reports their state.

    Defaults to checking the current directory, but you can pass a path to check."""

    if debug:
        logger.remove()
        logger.add(sink=sys.stdout, level="DEBUG")

    process_paths(path, short)


if __name__ == "__main__":
    cli()
