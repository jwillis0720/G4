"""Unit tests for analysis interface."""
import logging

import pytest
from click.testing import CliRunner

logger = logging.getLogger()


def test_cli() -> None:
    cli_runner = CliRunner()
    result = cli_runner.invoke("g4", "run")
    assert result.exit_code == 0