#!/usr/bin/env python
from setuptools import setup


def read_long_description(filename="README.rst"):
    with open(filename) as f:
        return f.readlines()


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()

setup(
    name="charlatan",
    version="0.1.1",
    author="Charles-Axel Dein",
    author_email="charles@uber.com",
    url="https://github.com/uber/charlatan",
    packages=["charlatan"],
    keywords=["tests", "fixtures", "database"],
    description="A Python library to efficiently manage and install database fixtures",
    long_description=read_long_description(),
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
