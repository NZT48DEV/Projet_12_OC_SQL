"""Helper pour exécuter la CLI Click en tests."""

from click.testing import CliRunner

from app.epicevents import cli


def invoke_cli(args: list[str]):
    """Exécute la CLI Click et retourne le résultat."""
    runner = CliRunner()
    return runner.invoke(cli, args)
