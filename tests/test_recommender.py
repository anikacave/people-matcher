from unittest.mock import patch

from lib.recommender import (
    load_mock_mentees,
    load_mock_mentors,
    generate_match_suggestions,
)
from tests.test_geo import address_to_location


def geocode_mock(addr):
    return address_to_location.get(addr)


def test_recommender_with_mock_data():
    df1 = load_mock_mentors().head(1)
    print(df1)
    df2 = load_mock_mentees().head(2)
    print(df2)
    with patch("lib.geo.rate_limited_geocode") as mocked:
        mocked.side_effect = geocode_mock
        match_suggestions = generate_match_suggestions(df1, df2)
    print("----------------------------------------")
    for s in match_suggestions:
        print(s[0], s[1]["name"], s[1].address, s[2]["name"], s[2].address)


def test_race_filter():
    df1 = load_mock_mentors().head(1)
    df2 = load_mock_mentees().head(2)
    print(df1)
    print(df2)
    match_suggestions = generate_match_suggestions(df1, df2, {"race": True})
    print("results from filtering by race")
    for s in match_suggestions:
        print(s)


