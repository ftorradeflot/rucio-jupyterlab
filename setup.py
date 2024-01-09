# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Muhammad Aditya Hilmy, <mhilmy@hey.com>, 2020

import json
import sys
from pathlib import Path
import logging

import setuptools
from setuptools.command.install import install

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "rucio_jupyterlab"

lab_path = (HERE / name.replace("-", "_") / "labextension")

# Representative files that should exist after a successful build
ensured_targets = [
    str(lab_path / "package.json"),
    str(lab_path / "static/style.js")
]

labext_name = "rucio-jupyterlab"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path.relative_to(HERE)), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str("."), "install.json"),
    ("etc/jupyter/jupyter_server_config.d",
     "jupyter-config/server-config", "rucio_jupyterlab.json"),
    # For backward compatibility with notebook server
    ("etc/jupyter/jupyter_notebook_config.d",
     "jupyter-config/nb-config", "rucio_jupyterlab.json"),
]

long_description = (HERE / "README.md").read_text()

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_bytes())


class CustomInstallation(install):
    
    def load_kernel_extension(self):
        '''Modify the system wide IPython configuration 
        to load the rucio-jupyterlab IPython extension at startup
        '''
        
        # Set path to config and ipython extension module
        config_folder = Path(sys.prefix) / 'etc' / 'ipython'
        file_path = config_folder / 'ipython_kernel_config.json'
        extension_module = 'rucio_jupyterlab.kernels.ipython'
    
        # Load the existing IPython kernel JSON configuration
        if not file_path.is_file():
            config_folder.mkdir(parents=True, exist_ok=True)
            config_json = {}
        else:
            with open(file_path, 'r') as f:
                config_payload = f.read()
            config_json = json.loads(config_payload)
    
        # Add the needed attributes to enable the extension
        if 'IPKernelApp' not in config_json:
            config_json['IPKernelApp'] = {}
    
        ipkernel_app = config_json['IPKernelApp']
    
        if 'extensions' not in ipkernel_app:
            ipkernel_app['extensions'] = []
    
        if extension_module not in ipkernel_app['extensions']:
            ipkernel_app['extensions'].append(extension_module)
    
        # Write the configuration back to the file
        with open(file_path, 'w') as f:
            f.write(json.dumps(config_json, indent=2))
    
    
    def run(self):
        try:
            logging.info('Try to load ipykernel extension by default')
            self.load_kernel_extension()
        except Exception as e:
            logging.error('An error occurred when loading the rucio_jupyterlab.kernels.ipython extension')
            logging.info(e, exc_info=True)
        
        install.run(self)


setup_args = dict(
    name=name,
    version=pkg_json["version"],
    url=pkg_json["homepage"],
    author=pkg_json["author"]["name"],
    author_email=pkg_json["author"]["email"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyter_server>=1.6,<2",
        "requests~=2.25.0",
        "peewee~=3.14.0",
        "jsonschema~=3.2.0",
        "psutil~=5.8.0",
        "rucio-clients>=1.26.0",
        "pyjwt"
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
        # These classifiers will be valid when https://github.com/pypa/warehouse/pull/9882 gets merged
        # "Framework :: Jupyter :: JupyterLab",
        # "Framework :: Jupyter :: JupyterLab :: 3",
        # "Framework :: Jupyter :: JupyterLab :: Extensions",
        # "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    ],
    cmdclass={'install': CustomInstallation},
)




try:
    from jupyter_packaging import (
        wrap_installers,
        npm_builder,
        get_data_files
    )
    post_develop = npm_builder(
        build_cmd="install:extension", source_dir="src", build_dir=lab_path
    )
    cmd_class_prebuild = wrap_installers(post_develop=post_develop, ensured_targets=ensured_targets)
    setup_args["cmdclass"].update(cmd_class_prebuild)
    setup_args["data_files"] = get_data_files(data_files_spec)
    logging.info(f'Setup args prepared')
except ImportError as e:

    logging.warning("Build tool `jupyter-packaging` is missing. Install it with pip or conda.")
    if not ("--name" in sys.argv or "--version" in sys.argv):
        raise e

if __name__ == "__main__":
    setuptools.setup(**setup_args)
