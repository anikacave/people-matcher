import pandas as pd
import re
import numpy as np
import base64
import datetime
import io

from lib.geo import geocode, get_distance
from lib.data_utils import (
    load_mock_mentees,
    load_mock_mentors,
    find_address_column,
    find_name_column,
)


# TODO: cache result in database
def to_location(addresses):
    locations = [geocode(a) for a in addresses]
    return locations


class PairwiseFeature(object):
    def __init__(self, query_row, match_row):
        self.query_row = query_row
        self.match_row = match_row

    @property
    def feature_names(self):
        return ["distance_in_miles", "ethnicity_match"]

    def to_dict(self):
        return dict([(f, getattr(self, f)) for f in self.feature_names])

    @property
    def distance_in_miles(self):
        return get_distance(self.query_row._point, self.match_row._point).miles

    @property
    def ethnicity_match(self):
        if (
            str(self.query_row.ethnicity) not in ["None", "", "NaN"]
            and self.query_row.ethnicity == self.match_row.ethnicity
        ):
            return 1
        else:
            return 0


def predict(fea):
    """TODO: make it trainable.
    """
    score = 10 - fea.distance_in_miles * 1 + fea.ethnicity_match * 2
    return dict(score=score, features=fea.to_dict())


def get_match_score(query_row, match_row):
    fea = PairwiseFeature(query_row, match_row)
    return predict(fea)


def get_match_scores(query_row, df):
    return [get_match_score(query_row, match_row) for _, match_row in df.iterrows()]


def generate_match_suggestions(df1, df2, options={}):
    """
    options: max_dinstance etc.
    """

    """
    Do stuff IDK
    """
    address_col1 = find_address_column(df1)
    assert address_col1 is not None, "Which column is address? {}".format(df1.columns)
    address_col2 = find_address_column(df2)
    assert address_col2 is not None, "Which column is address? {}".format(df2.columns)
    locations1 = to_location(df1[address_col1])
    locations2 = to_location(df2[address_col2])
    df1 = df1.assign(**{"_lat": [l.latitude for l in locations1]})
    df1 = df1.assign(**{"_lon": [l.longitude for l in locations1]})
    df1 = df1.assign(_point=[l.point for l in locations1])
    df2 = df2.assign(_point=[l.point for l in locations2])
    df2 = df2.assign(**{"_lat": [l.latitude for l in locations2]})
    df2 = df2.assign(**{"_lon": [l.longitude for l in locations2]})
    match_suggestions = []
    min_score = -100
    for _, row1 in df1.iterrows():
        score_objs = get_match_scores(row1, df2)
        for i, score_obj in enumerate(score_objs):
            # filter by race if race option enabled
            if("race" in options):
                if(options["race"] and not score_obj["features"]["ethnicity_match"]):
                    continue


            # filter by score
            if score_obj["score"] > min_score:
                match_suggestions.append(
                    (score_obj["score"], row1, df2.iloc[i], score_obj["features"])
                )

    match_suggestions = sorted(match_suggestions, key=lambda s: -s[0])

    return list(match_suggestions)







def sanity_check():
    df1 = load_mock_mentors()
    print(df1)
    df2 = load_mock_mentees()
    print(df2)
    match_suggestions = generate_match_suggestions(df1, df2)
    print("----------------------------------------")
    for s in match_suggestions:
        print(s[0], s[1]["name"], s[1].address, s[2]["name"], s[2].address)


if __name__ == "__main__":
    sanity_check()
