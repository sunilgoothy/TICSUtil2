from setuptools import setup, find_packages

setup(
    name="TICSUtil2",
    version="2.1.1",
    description="This package is a library of small functions used in TICS development.",
    author="Sunil Goothy",
    author_email="sunil.goothy@tmeic.in",
    install_requires=["loguru", "pyyaml", "rsa", "psutil"],
    packages=find_packages(),
)
