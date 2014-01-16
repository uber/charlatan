#!/usr/bin/env python
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


def read_long_description(filename="README.rst"):
    with open(filename) as f:
        return f.read().strip()


def read_requirements(filename="requirements.txt"):
    with open(filename) as f:
        return f.readlines()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name="charlatan",
    version='0.3.2',
    author="Charles-Axel Dein",
    author_email="charles@uber.com",
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    url="https://github.com/uber/charlatan",
    packages=["charlatan"],
    keywords=["tests", "fixtures", "database"],
    description="Efficiently manage and install data fixtures",
    long_description=read_long_description(),
    install_requires=read_requirements(),
    zip_safe=False,
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
