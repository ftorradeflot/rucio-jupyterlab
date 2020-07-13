# Rucio JupyterLab Extension

![Github Actions Status](https://github.com/didithilmy/rucio-jupyterlab/workflows/Build/badge.svg)

This is a JupyterLab extension that integrates with [Rucio - Scientific Data Management](https://github.com/rucio/rucio) to allow users to access some of Rucio's capabilities directly from the JupyterLab interface.


This extension is composed of a Python package named `rucio_jupyterlab`
for the server extension and a NPM package named `rucio-jupyterlab`
for the frontend extension.


## Requirements

* JupyterLab >= 2.0

## Install

Note: You will need NodeJS to install the extension.

```bash
pip install rucio-jupyterlab
jupyter lab build
```

Restart your JupyterLab instance afterwards to load the server extension.

## Configuration

See [CONFIGURATION.md](CONFIGURATION.md)

## Contributing

If you want to contribute or build the extension from source, see [CONTRIBUTING.md](CONTRIBUTING.md)

## Quick Setup using Docker

This repository comes with a Docker image of [jupyter/scipy-notebook](https://hub.docker.com/r/jupyter/scipy-notebook) installed with the extension.

To run the image, use the following command.
```bash
$ docker run -d -p 8888:8888 \
    -e RUCIO_BASE_URL=<Rucio base URL> \
    -e RUCIO_DESTINATION_RSE=<destination RSE> \
    -e RUCIO_DISPLAY_NAME=<instance display name> \
    -e RUCIO_NAME=<instance name> \
    -e RUCIO_PATH_BEGINS_AT=<path begins at> \
    -e RUCIO_RSE_MOUNT_PATH=<mount path> \
    -v <host folder>:<container folder> \
    didithilmy/rucio-jupyterlab:latest
```

Follow the [configuration guide](CONFIGURATION.md) for details of the parameters.


`<host folder>` is a folder in the host that is mounted to a Rucio Storage Element via FUSE.
`<container folder>` is a folder accessible from the notebook that is mounted to the host folder.

## Troubleshoot

If you are seeing the frontend extension but it is not working, check
that the server extension is enabled:

```bash
jupyter serverextension list
```

If the server extension is installed and enabled but you are not seeing
the frontend, check the frontend is installed:

```bash
jupyter labextension list
```

If it is installed, try:

```bash
jupyter lab clean
jupyter lab build
```