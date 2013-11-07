from fabric.api import local, task, lcd
from fabric.colors import green


@task
def test(args=""):
    """Run the test suite."""

    clean()
    local("flake8 charlatan/ --ignore=E501,E702")
    local(
        "nosetests --with-doctest --with-coverage --cover-erase --cover-html "
        "--cover-package=charlatan"
    )
    with lcd("docs"):
        local("make doctest")


@task
def clean():
    """Remove all .pyc files"""
    # Ignore hidden files and folder
    local("find . \( ! -regex '.*/\..*/..*' \) -type f -name '*.pyc' -exec rm '{}' +")


@task
def docs():
    """Generate documentation."""

    print green("\nGenerating documentation...")

    local("python setup.py develop")
    with lcd("docs"):
        local("make html BUILDDIR=../../charlatan-docs")


@task
def open_docs():
    """Generate and open the docs."""

    docs()
    local("open ../charlatan-docs/html/index.html")


@task
def release():
    """Prepare a release."""

    print green("\nRunning prerelease...")
    test()
    docs()
    local("prerelease")

    print green("\nReleasing...")
    local("release")
    local("git push --tags")
    local("git push")
