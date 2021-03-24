# git_project_status

Real simple, just iterates through the first-level subdirectories and does the equivalent of git status, only uglier.

If you want more logs, set an environment variable of `LOGURU_LOG_LEVEL=DEBUG`.

Installation: `pip install git-project-status`

Which will create a console script `git_project_status`.

[![Build Status](https://droneio.yaleman.org/api/badges/yaleman/git_project_status/status.svg)](https://droneio.yaleman.org/yaleman/git_project_status)

## Changelog

 * 0.0.6 - Fixed handling detached heads.