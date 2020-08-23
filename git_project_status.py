#!/usr/bin/env python3

""" scans the local directory for sub-directories that have git repos in them, then does a git status on them """

import os
from git import Repo
import git.exc

dirlist = os.listdir("./")

if not os.environ.get('LOGURU_LEVEL'):
    os.environ['LOGURU_LEVEL'] = 'INFO'

if os.environ.get('LOGURU_LEVEL') == 'INFO':
    os.environ['LOGURU_FORMAT'] = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>'


from loguru import logger

def handle_diff(repo_object, compare=None, message="Changes"):
    """ does the needful """
    if repo_object.head.commit.diff(compare):
        logger.info(f"{message}:")
        for diff_added in repo.head.commit.diff(compare):
            if diff_added.renamed:
                logger.info(f'renamed : {diff_added.rename_from} -> {diff_added.rename_to}')
            elif diff_added.new_file:
                logger.info(f"new file: {diff_added.b_path}")
            elif diff_added.change_type == 'M':
                logger.info(f"modified: {diff_added.b_path}")
            elif diff_added.change_type == 'D':
                logger.info(f'deleted:  {diff_added.b_path}')
            else:
                logger.error(f"Unknown change type: '{diff_added.change_type}'")
                logger.error(diff_added)
                logger.debug(dir(diff_added))

for filename in dirlist:
    dirpath = f"./{filename}"
    if os.path.isdir(dirpath):
        logger.debug(f"Found dir: {dirpath}")
        try:
            repo = Repo(dirpath)
        except git.exc.InvalidGitRepositoryError as error_message:
            logger.debug(f"{dirpath} is not a repository, skipping ({error_message})")
            continue
        if repo.bare:
            logger.info(f"{dirpath} is bare, ignoring.")
            continue

        if repo.is_dirty():
            logger.warning(f"{dirpath} ({repo.active_branch}) dirty")
            if repo.untracked_files:
                logger.info("Untracked files:")
                for filename in repo.untracked_files:
                    logger.info(f"{filename}")
            
            handle_diff(repo, compare='HEAD', message='Changes staged for commit')
            handle_diff(repo, compare=None, message='Changes not staged for commit')

            logger.info("")
            
            #logger.debug(dir(repo))
            #for branch in repo.branches:
             #   logger.debug(dir(branch))
            continue