import os
from dataclasses import dataclass
import subprocess

import click
import yaml


@dataclass
class Config:
    config_dir: str
    kubeconfig: str

    @classmethod
    def from_source(cls, config_path, env):
        with open(config_path) as f:
            raw = yaml.load(f, yaml.SafeLoader)
            default_raw = raw.get("default", {})
            env_raw = raw.get("envs", {}).get(env, {})

            merged = {
                **default_raw,
                **env_raw,
            }

            # TODO: better error handling...
            cleaned = {
                **merged,
                "config_dir": os.path.abspath(merged["config_dir"]),
                "kubeconfig": os.path.abspath(os.path.join(merged["config_dir"], merged["kubeconfig"])),
            }

            return Config(**cleaned)


@click.group()
@click.option("--config", type=click.Path(resolve_path=True), default="./.k8senv.yaml")
@click.option("--verbose", "-v", default=False, is_flag=True)
@click.pass_context
def cli(ctx, config, verbose):
    ctx.ensure_object(dict)

    ctx.obj["k8senv_config_path"] = config
    ctx.obj["verbose"] = verbose


@cli.command("init")
@click.option("--env", multiple=True, default=["prod", "stage"], help="The environment names to initialise")
@click.option("--update-gitignore/--no-update-gitignore", default=True, help="Flag to add the config dir to gitignore")
@click.option("--config-dir", default="./.kube", help="Flag to add the config dir to gitignore")
@click.option("--force/--no-force", default=False, help="Flag to override the existing config if it exists")
@click.pass_context
def init(ctx, env, update_gitignore, config_dir, force):
    if not force and os.path.exists(ctx.obj["k8senv_config_path"]):
        click.echo(
            f"Path {ctx.obj['k8senv_config_path']} already exists, either remove it, provide a different config path "
            "using --config or use the --force flag to override the existing config",
            err=True,
        )
        return 1

    # build and write out the config
    config = {
        "default": {
            "config_dir": config_dir,
        },
        "envs": {
            e: {
                "kubeconfig": e
            } for e in env
        }
    }

    with open(ctx.obj["k8senv_config_path"], "w") as f:
        yaml.dump(config, f)

    # create the root kube config dir
    os.makedirs(config_dir, exist_ok=True)
    with open(os.path.join(config_dir, "README.md"), "w") as f:
        f.write(
            "Use this directory to store all of your kube configs for this project. "
            "Each file name should match the environment name by default."
        )

    # add the config dir to the gitignore if flagged to do so
    if update_gitignore:
        config_dir_parent = os.path.dirname(config_dir)

        with open(os.path.join(config_dir_parent, ".gitignore"), "a") as f:
            f.writelines([
                "\n",
                f"{config_dir}/*",
                f"!{config_dir}/README.md",
                "\n"
            ])


@cli.command()
@click.argument("env")
@click.argument("cmd", nargs=-1)
@click.pass_context
def run(ctx, env, cmd):
    config = Config.from_source(ctx.obj["k8senv_config_path"], env)

    command = [
        "kubectl",
        f"--kubeconfig={config.kubeconfig}",
        *cmd,
    ]

    if ctx.obj["verbose"]:
        click.echo(f"Running command '{' '.join(command)}'")

    return subprocess.run(command)
