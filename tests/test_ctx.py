import json
import os.path

import click
from click.testing import CliRunner

from k8senv import cli


@cli.command()
@click.pass_context
def cmd(ctx):
    click.echo(json.dumps(ctx.obj))


def test_config_path_is_not_provided___default_config_path_is_added_to_the_context():
    runner = CliRunner()

    result = runner.invoke(cli, ["cmd"])
    obj = json.loads(result.output)

    assert obj["k8senv_config_path"] == os.path.abspath("./.k8senv.yaml")


def test_config_path_is_provided___config_path_is_added_to_the_context():
    runner = CliRunner()

    result = runner.invoke(cli, ["--config=./other.config", "cmd"])
    obj = json.loads(result.output)

    assert obj["k8senv_config_path"] == os.path.abspath("./other.config")


def test_verbose_is_not_provided___default_verbose_is_added_to_the_context():
    runner = CliRunner()

    result = runner.invoke(cli, ["cmd"])
    obj = json.loads(result.output)

    assert obj["verbose"] is False


def test_verose_is_provided___verbose_is_added_to_the_context():
    runner = CliRunner()

    result = runner.invoke(cli, ["--verbose", "cmd"])
    obj = json.loads(result.output)

    assert obj["verbose"] is True
