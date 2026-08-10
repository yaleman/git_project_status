"""tests not much"""

from pathlib import Path

from click.testing import CliRunner
from git import Repo

from git_project_status.__main__ import cli, process_paths
from git_project_status import count_unpushed_commits


def test_cli_runs() -> None:
    """tests the CLI runs locally"""
    for short in [True, False]:
        process_paths(".", short)


def test_cli_working() -> None:
    """tests it runs locally"""
    runner = CliRunner()
    result = runner.invoke(cli, ["."])
    assert result.exit_code == 0
    result = runner.invoke(cli, [".asdfasdf"])
    assert result.exit_code == 2


def _init_repo(repo_path: Path) -> Repo:
    repo = Repo.init(repo_path)
    with repo.config_writer() as config:
        config.set_value("user", "name", "test")
        config.set_value("user", "email", "test@example.com")
    return repo


def test_unpushed_commits(tmp_path: Path) -> None:
    """tests detection of commits ahead of upstream"""
    remote = tmp_path / "remote.git"
    Repo.init(remote, bare=True)

    repo = _init_repo(tmp_path / "repo")
    (tmp_path / "repo" / "first.txt").write_text("first")
    repo.index.add(["first.txt"])
    repo.index.commit("initial commit")

    repo.create_remote("origin", str(remote))
    repo.git.push("--set-upstream", "origin", repo.active_branch.name)
    assert count_unpushed_commits(repo) == 0

    (tmp_path / "repo" / "second.txt").write_text("second")
    repo.index.add(["second.txt"])
    repo.index.commit("second commit")
    assert count_unpushed_commits(repo) == 1


def test_unpushed_commits_without_remote(tmp_path: Path) -> None:
    """tests unpushed count is skipped when no upstream exists"""
    repo = _init_repo(tmp_path / "repo")
    (tmp_path / "repo" / "first.txt").write_text("first")
    repo.index.add(["first.txt"])
    repo.index.commit("initial commit")
    assert count_unpushed_commits(repo) is None
