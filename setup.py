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
    version='0.3.8',
    author="Charles-Axel Dein",
    author_email="charles@uber.com",
    license="MIT",
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
