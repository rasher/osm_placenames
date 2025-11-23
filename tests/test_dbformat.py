import pytest

from osm_placenames.dbformat import cleanup_description, cleanup_wp

WP_EN = 'https://en.wikipedia/wiki/'

@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("village in Yorkshire", "Village in Yorkshire"),
        (" \n", ""),
        ("Test\u200e", "Test"),
        ("capital and largest city of England and the United Kingdom", "Capital and largest city of England"),
        ("village in West Sussex, England, UK", "Village in West Sussex"),
        ("market town in Huntingdonshire, Cambridgeshire, UK", "Market town in Huntingdonshire, Cambridgeshire"),
        ("town and civil parish in Wiltshire, England", "Town in Wiltshire"),
    ],
)
def test_cleanup_description(input, expected):
    assert cleanup_description(input) == expected

@pytest.mark.parametrize(
    ("input", "expected"),
    [
        (WP_EN + "", WP_EN + ""),
        (WP_EN + "London", WP_EN + "London"),
        (WP_EN + "Narborough%2C+Norfolk", WP_EN + "Narborough%2C_Norfolk"),
        (WP_EN + "Morley+Saint+Peter", WP_EN + "Morley_Saint_Peter"),
        (WP_EN + "Ashley (Hampshire)", WP_EN + "Ashley_%28Hampshire%29"),
        (WP_EN + "Raymond's_Hill", WP_EN + "Raymond%27s_Hill"),
    ],
)
def test_cleanup_wp(input, expected):
    assert cleanup_wp(input) == expected
