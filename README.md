k8senv
======

Helps you manage multiple kubernetes cluster configs to prevent performing
commands on the wrong cluster.

Installation
------------

```shell
$> pip install -e git+ssh://git@github.com/wildfish/k8senv.git#egg=k8senv
```

Setup
-----

To initialise the configuration run:

```shell
$> k8senv init
```

This will create the `.k8senv.yaml` file along with the `.kube` directory in 
the current directory as well as adding the relevant entries to the `.gitignore`
file.

By default, the config will be setup for 2 environments, `prod` and `stage`.
This can be overridden by providing any number of `--env` arguments.

Once the config is setup you will need to generate your kube configs based
on the instructions of your provider and move the entry to the relevant file
in the `.kube` directory.

For example, using k3d, to save the cluster to the stage config run:

```shell
$> KUBECONFIG="./.kube/stage.yaml" k3d cluster create test
```

or:

```shell
$> k3d kubeconfig get test > ./.kube/stage.yaml
```

```
Usage: k8senv init [OPTIONS]

  Initialises the k8senv config

Options:
  --env TEXT                      The environment names to initialise
  --update-gitignore / --no-update-gitignore
                                  Flag to add the config dir to gitignore
  --config-dir TEXT               The directory to store the cluster configs
  --force / --no-force            Flag to override the existing config if it
                                  exists
  --help                          Show this message and exit.
```

Running
-------

To run a kubernetes command use:

```shell
$> k8senv run <env> -- <command>
```

The env should match the name of one of the environments in the config. The
command should match the command that would normally be passed to `kubectl`.

For example, to print the config for the stage environment run:

```shell
$> k8senv run stage -- config view
```

To view all pods in the prod environment run: 

```shell
$> k8senv run prod -- get pod
```

The configs are normal kubernetes configs so anything you can do with kubectl
can be done with k8senv (it's just a wrapper after all). So to further 
configure the environment such as adding a namespace you can just run the same
`kubectl` commands. For example:

```shell
$> k8senv -v run stage -- config set-context --current --namespace=stage-ns
```

Will set the namespace in the config to `stage-ns`.

```
Usage: k8senv run [OPTIONS] ENV [CMD]...

Options:
  --help  Show this message and exit.
```

Listing
-------

To list all the available configured environments run:

```shell
$> k8senv ls
```

This will print all the environment names along with some validation:

```
local
prod (config error)
stage (cluster config file missing)
```

**NOTE:** No validation is performed on the cluster config, only the k8senv config.

```
Usage: k8senv ls [OPTIONS]

Options:
  --help  Show this message and exit
```
