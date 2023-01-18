import os.path

import yaml
from click.testing import CliRunner

from k8senv import cli


def test_config_doesnt_exist___default_config_is_created():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init"])

        with open("./.k8senv.yaml") as f:
            config = yaml.load(f, yaml.SafeLoader)

        assert config == {
            "default": {
                "config_dir": ".kube",
            },
            "envs": {
                "stage": {"kubeconfig": "stage.yaml"},
                "prod": {"kubeconfig": "prod.yaml"},
            },
        }


def test_config_does_exist_force_isnt_set___error_is_raised():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./.k8senv.yaml", "w") as f:
            f.write("existing config")

        result = runner.invoke(cli, ["init"])

        with open("./.k8senv.yaml") as f:
            assert f.read() == "existing config"

        assert result.exit_code == 1
        assert (
            f"Path {os.path.abspath('./.k8senv.yaml')} already exists, either remove it, provide a different config path "
            "using --config or use the --force flag to override the existing config"
            in result.output
        )


def test_config_does_exist_force_is_set___config_is_replaced():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./.k8senv.yaml", "w") as f:
            f.write("existing config")

        result = runner.invoke(cli, ["init", "--force"])

        with open("./.k8senv.yaml") as f:
            config = yaml.load(f, yaml.SafeLoader)

        assert result.exit_code == 0
        assert config == {
            "default": {
                "config_dir": ".kube",
            },
            "envs": {
                "stage": {"kubeconfig": "stage.yaml"},
                "prod": {"kubeconfig": "prod.yaml"},
            },
        }


def test_envs_are_provided___config_is_created():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init", "--env=first", "--env=second"])

        with open("./.k8senv.yaml") as f:
            config = yaml.load(f, yaml.SafeLoader)

        assert config == {
            "default": {
                "config_dir": ".kube",
            },
            "envs": {
                "first": {"kubeconfig": "first.yaml"},
                "second": {"kubeconfig": "second.yaml"},
            },
        }


def test_config_dir_is_provided___config_is_created():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init", "--config-dir=./other/config/dir"])

        with open("./.k8senv.yaml") as f:
            config = yaml.load(f, yaml.SafeLoader)

        assert config == {
            "default": {
                "config_dir": "./other/config/dir",
            },
            "envs": {
                "stage": {"kubeconfig": "stage.yaml"},
                "prod": {"kubeconfig": "prod.yaml"},
            },
        }


def test_gitignore_doesnt_exist___gitignore_is_created():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init"])

        with open("./.gitignore") as f:
            assert [
                "",
                ".kube/*",
                "!.kube/README.md",
                "",
            ] == f.read().split("\n")


def test_gitignore_exists___gitignore_is_appended_to():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./.gitignore", "w") as f:
            f.writelines(["orig\n"])

        runner.invoke(cli, ["init"])

        with open("./.gitignore") as f:
            assert [
                "orig",
                "",
                ".kube/*",
                "!.kube/README.md",
                "",
            ] == f.read().split("\n")


def test_gitignore_doesnt_exist_dont_create_flag_is_set___gitignore_is_not_created():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init", "--no-update-gitignore"])

        assert not os.path.exists("./.gitignore")
