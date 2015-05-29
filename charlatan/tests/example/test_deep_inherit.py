from charlatan import FixturesManager


def test_deep_inherit():
    manager = FixturesManager()
    manager.load('./charlatan/tests/example/data/deep_inherit.yaml')
    toaster2 = manager.get_fixture('toaster2')
    assert toaster2['toasts']['toast1']['price'] == 10
    assert toaster2['toasts']['toast1']['weight'] == 20
