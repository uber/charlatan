import pytest

from charlatan import file_format


def test_non_yaml_file():
    """Verify that we can't open a non-YAML file."""
    with pytest.raises(ValueError):
        file_format.load_file("./charlatan/tests/data/test.json")
