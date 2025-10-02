# Rucio jupyterlab extension test environment

## Overview

This folder contains the necessary files and instructions to launch
a local Rucio cluster with the goal of testing the jupyterlab extension 
coupled to specific versions of Rucio and jupyterlab.

The cluster is an extension of the
[Rucio development cluster](https://github.com/rucio/rucio/tree/master/etc/docker/dev)
with an additional container (`rucio-jupyterlab`) containing a jupyterlab server 
with the checked-out version of the Rucio jupyterlab extension.

## Preparation

### Build the rucio-jupyterlab docker image

Check the documentation in the [container folder](../container/README.md)

### Choose the version of Rucio

Rucio is added as a git submodule.

If it's the first time you clone this repo,
you will have to run `git submodule init` to initialize it, and `git submodule update` to fetch
the updates.

Then you can choose the version of Rucio you want to use by doing a `git checkout`, for example:
```
cd rucio
git checkout 32.8.0
```


## Managing the development cluster

### Start the cluster

Execute the `run_test_env.sh` script to launch a development cluster.

This script will also create a temporary folder in `$TMP` (`/tmp/rucio_xrd1`) that will be shared between
the XRD1 RSE and the jupyterlab container to test the extension in `replica` mode.

The script also runs the tests to create some dummy data. If the temporary folder already exists,
it is assumed that the dummy data was already created and this step is skipped.

Once the script is executed it will take some time for the rucio-jupyterlab container
to be ready. It has to install all the dependencies, build the extension, ...
The progress of the setup can be tracked through the container logs
`docker logs -t dev-rucio-jupyterlab-1` . When the process finishes there will be 
this message in the logs
```
[I 2024-02-08 12:42:04.428 ServerApp] Jupyter Server 1.24.0 is running at:
[I 2024-02-08 12:42:04.428 ServerApp] http://693c5ea2930d:8888/lab
[I 2024-02-08 12:42:04.428 ServerApp]  or http://127.0.0.1:8888/lab
[I 2024-02-08 12:42:04.428 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```
and the jupyterlab server will be accessible at http://localhost:8888


### Stop the cluster

Execute the `stop_test_env.sh` script to stop de cluster,
remove the containers and the temporary directory.


## Testing the extension

### Accessing the jupyterlab server

Once the development cluster is running, the jupyerlab server should be reachable
through a web browser at http://localhost:8888

### Check Rucio

From a terminal in jupyterlab you can check that the Rucio credentials are correct:

    rucio whoami

Perform other rucio commands at your wish, for example: 

		rucio list-dids --filter 'type=all' test:*

will list all DIDs in the `test` scope.

When starting the dev cluster, some replication rules will be
created but they will be stuck in `REPLICATING`.
See the section on [How to trigger replicas](#how-to-trigger-replicas)

### Testing the extension

* Go to the Rucio jupyterlab extension dashboard no the left-side panel.
* Fill in the Settings:
  * Active Instance = "Rucio Test"
  * Authentication = "Username & Password"
  * Username = "ddmlab"
  * Password = "secret"
  * Account = "root"
* Go to the **Explore** tab, look for `test:file3` and then click on "Make Available"
  * If the extension is working in `download` mode
  the file should be available locally after some minutes
  * If the extension is working in `replica` mode a replication rule will 
  be added but the replication process will be stuck because there are no Rucio daemons
  in the dev cluster see the section [How to trigger replicas](#how-to-trigger-replicas)
* Once the file is "Available", open a Notebook
* The "Add to Notebook" button should appear next to the "Available" label,
click on it and follow the steps to add an environment variable containing the path to the 
DID in the notebook
* A green "Ready" label should be visible in the top bar of the notebook
* The attached DIDs should be listed in the Notebook tab of the Rucio jupyterlab extension dashboard


## Troubleshooting

### How to trigger replicas

When using the development cluster, the daemons are not deployed so you have to run them
in single execution mode to actually get the replication done.

Open a terminal inside the `dev-rucio-1` container by running this command
in the host machine (not in jupyterlab)

    docker exec -it dev-rucio-1 /bin/bash

Then run these commands

    rucio-conveyor-submitter --run-once
    rucio-conveyor-poller --run-once --older-than 0
    rucio-conveyor-finisher --run-once

## OIDC authentication

If you want to use OIDC authentication you have to request a token from IndigoIAM

### Accessing services in the cluster

To be able to access services running in the test cluster (IndigoIAM, Rucio & Keycloak) through the nginx proxy,
you need to add this content to the `/etc/hosts` file in your computer:

```
127.0.0.1 indigoiam
127.0.0.1 keycloak
127.0.0.1 rucio
```

### Get an OIDC token with IndigoIAM

Execute the `get-access-token-password.sh` script to get a token and write it in the `rucio_token` file. This file is mounted inside the rucio-jupyterlab container, although you might need to restart the container to make it available.

Take care to update the client id and the secret if needed.

You can access the indigoiam at `https://indigoiam:443` with `admin:password` credentials,
and check the client id and secret.

Also the redirect uris have to be set:
* https://rucio/auth/oidc_token
* https://rucio/auth/oidc_code

### Log in to Rucio with OIDC

Add OIDC identity to root account if it's not already there

```
rucio-admin identity add --account root --type OIDC --id "SUB=73f16d93-2441-4a50-88ff-85360d78c6b5, ISS=https://indigoiam/" --email admin@iam.test
```

Log in using OIDC

```
rucio -S oidc --oidc-scope ruciodev --oidc-issuer indigoiam --oidc-scope "openid profile" --oidc-audience rucio -vvv whoami
```

which will redirect you to the browser. Or
```
rucio -S oidc --oidc-auto --oidc-user admin --oidc-password password --oidc-scope ruciodev --oidc-issuer indigoiam --oidc-scope "openid profile" --oidc-audience rucio -vvv whoami
```









