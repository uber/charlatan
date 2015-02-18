from charlatan import FixturesManager
from charlatan.builder import Builder


class Toaster(object):

    def __init__(self, attrs):
        self.slots = attrs['slots']


class DictBuilder(Builder):

    def __call__(self, fixtures, klass, params, **kwargs):
        # A "normal" object would be instantiated this way:
        # return klass(**params)

        # Yet schematics object expect a dict of attributes as only argument.
        # So we'll do:
        return klass(params)


def test_custom_builder():
    manager = FixturesManager(get_builder=DictBuilder())
    manager.load('./charlatan/tests/example/data/custom_builder.yaml')
    assert manager.get_fixture('toaster').slots == 3
