from __future__ import absolute_import
import datetime

import yaml

from charlatan.utils import apply_delta


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
        """Return the current datetime."""

        delta = loader.construct_scalar(node)
        now = datetime.datetime.utcnow()

        if delta:
            now = apply_delta(now, delta)

        return now

    def relationship_constructor(loader, node):
        """Create _RelationshipToken for `!rel` tags."""

        name = loader.construct_scalar(node)
        return RelationshipToken(name)

    yaml.add_constructor(u'!now', now_constructor)
    yaml.add_constructor(u'!rel', relationship_constructor)


def load_file(filename):
    """Load fixtures definition from file.

    :param str filename:
    """

    with open(filename) as f:
        content = f.read()

    if filename.endswith(".yaml"):
        # Load the custom YAML tags
        configure_yaml()
        content = yaml.load(content)
    else:
        raise KeyError("Unsupported filetype: '%s'" % filename)

    return content
