import os.path
from unittest.mock import patch

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


def test_env_is_not_provided___command_is_not_ran(runner):
    with patch("k8senv.subprocess") as mock_sub_process:
        res = runner.invoke(cli, ["run", "--", "help"])

        assert res.exit_code == 1
        mock_sub_process.run.assert_not_called()


def test_command_is_not_provided___command_is_not_ran(runner):
    with patch("k8senv.subprocess") as mock_sub_process:
        res = runner.invoke(cli, ["run", "stage"])

        assert res.exit_code == 1
        mock_sub_process.run.assert_not_called()


def test_command_and_env_are_provided___command_is_ran_with_correct_config(runner):
    with patch("k8senv.subprocess") as mock_sub_process:
        runner.invoke(cli, ["run", "stage", "--", "help"])

        mock_sub_process.run.assert_called_once_with(
            [
                "kubectl",
                f"--kubeconfig={os.path.abspath(os.path.join('./.kube/', config_file_name))}",
                "help",
            ]
        )
