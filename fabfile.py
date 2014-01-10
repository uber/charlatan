from fabric.api import local, task, lcd
from fabric.colors import green


@task
def test():
    """Run the test suite."""

    clean()
    local("flake8 charlatan/ --ignore=E501,E702")
    local("python setup.py test")


@task
def tu(args=""):
    """Run the unit test suite."""
    clean()
    local("py.test %s" % args)


@task
def coverage():
    """Run the coverage."""
    local("coverage run --source charlatan setup.py test")
    local("coverage report -m")
    local("coverage html")
    local("open htmlcov/index.html")


@task
def clean():
    """Remove all .pyc files."""
    # Ignore hidden files and folder
    local("find . -name '*.py[co]' -exec rm -f '{}' ';'")


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
