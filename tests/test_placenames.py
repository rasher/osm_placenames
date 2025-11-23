import pytest

from osm_placenames.placenames import get_wikipedia


@pytest.fixture
def mocked_node():
    class MockNode:
        tags = {}

    return MockNode()


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("en:London", "https://en.wikipedia.org/wiki/London"),
        ("en:Burley, Hampshire", "https://en.wikipedia.org/wiki/Burley%2C_Hampshire"),
        ("da:Foo", "https://da.wikipedia.org/wiki/Foo"),
        ("Not matching", "Not matching"),
        ("", ""),
        (None, None),
    ],
)
def test_get_wikipedia(mocked_node, input, expected):
    mocked_node.tags["wikipedia"] = input
    assert get_wikipedia(mocked_node).get("wikipedia") == expected
