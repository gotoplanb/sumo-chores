#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="sumo-chores",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "rich",
        "typer",
        "pygithub",
    ],
    python_requires=">=3.8",
) 