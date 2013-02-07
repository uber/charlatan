from fabric.api import local, task, lcd
from fabric.colors import green


@task
def test(args=""):
    """Run the test suite."""

    clean()
    local("flake8 charlatan/ --ignore=E501,E702")
    local("nosetests --with-doctest")


@task
def clean():
    """Remove all .pyc files"""

    # Ignore hidden files and folder
    local("find . \( ! -regex '.*/\..*/..*' \) -type f -name '*.pyc' -exec rm '{}' +")


@task
def doc():
    """Generate documentation."""

    with lcd("docs"):
        local("make html BUILDDIR=../../charlatan-docs")

    print green("Don't forget to push the changes to the gh-pages branch.")
