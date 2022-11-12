""" tests not much """
from click.testing import CliRunner

from git_project_status.__main__ import cli, process_paths

def test_cli_runs() -> None:
    """ tests the CLI runs locally """
    process_paths(".")


def test_cli_working() -> None:
    """ tests it runs locally """
    runner = CliRunner()
    result = runner.invoke(cli, ['.'])
    assert result.exit_code == 0
    result = runner.invoke(cli, ['.asdfasdf'])
    assert result.exit_code == 2
