from __future__ import absolute_import
import datetime

import yaml
from yaml.constructor import Constructor

from charlatan.utils import get_timedelta, datetime_to_epoch_timestamp


class RelationshipToken(str):
    """Class used to mark relationships.

    This token is used to mark relationships found in YAML file, so that they
    can be processed later.
    """
    pass


class UnnamedRelationshipToken(dict):
    """Class used to mark unamed relationships.

    This token is used to mark relationships found in YAML file, so that they
    can be processed later.
    """
    pass


def configure_yaml():
    """Add some custom tags to the YAML constructor."""

    def now_constructor(loader, node):
        """Return a function that returns the current datetime."""
        delta = get_timedelta(loader.construct_scalar(node))

        def get_now():
            return datetime.datetime.utcnow() + delta

        return get_now

    def epoch_now_constructor(loader, node):
        """Return a function that returns the current epoch."""
        delta = get_timedelta(loader.construct_scalar(node))

        def get_now():
            return datetime_to_epoch_timestamp(
                datetime.datetime.utcnow() + delta)

        return get_now

    def relationship_constructor(loader, node):
        """Create _RelationshipToken for `!rel` tags."""
        name = loader.construct_scalar(node)
        return RelationshipToken(name)

    yaml.add_constructor(u'!now', now_constructor)
    yaml.add_constructor(u'!epoch_now', epoch_now_constructor)
    yaml.add_constructor(u'!rel', relationship_constructor)


def configure_output(use_unicode=False):
    """Configure output options of the values loaded by pyyaml

    :param bool use_unicode: Use unicode constructor for loading strings
    """
    if use_unicode:
        yaml.add_constructor(
            u'tag:yaml.org,2002:str',
            Constructor.construct_python_unicode,
        )


def load_file(filename, use_unicode=False):
    """Load fixtures definition from file.

    :param str filename:
    """

    with open(filename) as f:
        content = f.read()

    if filename.endswith(".yaml"):
        # Load the custom YAML tags
        configure_yaml()
        configure_output(use_unicode=use_unicode)
        content = yaml.load(content)
    else:
        raise ValueError("Unsupported filetype: '%s'" % filename)

    return content
