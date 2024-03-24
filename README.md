# Pypi Faker

This project aims to generate mock PyPI packages
to bypass the installation of specific packages.

This can be particularly helpful when you need to install a package
that has numerous dependencies, but you wish to exclude certain packages from the installation process.


## Usage

```
pip uninstall -y torch
pip install https://pypi-faker.homeinfra.org/targz/torch/2.0
pip install https://pypi-faker.homeinfra.org/targz/torchvision/0.17
# or use the following one
pip install "torch==2.0.0" "torchvision==0.17" -i https://pypi-faker.homeinfra.org

# verify the installed fake package
pip list | grep torch

```
