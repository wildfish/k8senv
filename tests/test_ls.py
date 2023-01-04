import json
import os.path
from unittest.mock import patch

import click
import pytest
import yaml
from click.testing import CliRunner

from k8senv import cli


config_file_name = "custom-config-name.yaml"


@pytest.fixture()
def runner():
    runner = CliRunner()

    with runner.isolated_filesystem():
        with open("./.k8senv.yaml", "w") as f:
            yaml.dump(
                {
                    "default": {
                        "config_dir": "./.kube",
                    },
                    "envs": {
                        "stage": {"kubeconfig": config_file_name},
                    },
                },
                stream=f,
            )

        yield runner


def test_config_is_bad___error_is_written_to_the_output(runner):
    with open("./.k8senv.yaml", "w") as f:
        yaml.dump({"envs": {"stage": {}}}, stream=f)

    res = runner.invoke(cli, ["ls"])

    assert res.exit_code == 0
    assert "stage (config error)" in res.output


def test_env_config_is_missing___error_is_written_to_the_output(runner):
    res = runner.invoke(cli, ["ls"])

    assert res.exit_code == 0
    assert "stage (cluster config file missing)" in res.output


def test_env_config_is_present___entry_is_written_to_output(runner):
    os.makedirs(".kube")
    with open(os.path.join(".kube", config_file_name), "w") as f:
        f.write("cluster conf")

    res = runner.invoke(cli, ["ls"])

    assert res.exit_code == 0
    assert "stage" in res.output
