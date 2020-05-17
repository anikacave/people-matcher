import pandas as pd
import re
import numpy as np
import base64
import datetime
import io
import json

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
    df1: mentors
    df2: mentees

    options: max_dinstance etc.
    """
    print("generate_match_suggestions:")
    print(df1[["name", "address"]].head(2))
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
    print(df1[["name", "address"]].head(2))
    match_suggestions = []
    min_score = -100
    for _, row1 in df1.iterrows():
        score_objs = get_match_scores(row1, df2)
        for i, score_obj in enumerate(score_objs):
            # filter by race if race option enabled
            if "race" in options:
                if options["race"] and not score_obj["features"]["ethnicity_match"]:
                    continue

            # filter by score
            if score_obj["score"] > min_score:
                status = "suggested"
                row2 = df2.iloc[i]
                match_suggestions.append(
                    dict(
                        score=score_obj["score"],
                        mentor_id=row1["id"],
                        mentor_name=row1[
                            "name"
                        ],  # using row1.name has strange side effects..
                        mentor_address=row1.address,
                        mentor_ethnicity=row1.ethnicity,
                        mentee_id=row2["id"],
                        mentee_name=row2["name"],
                        mentee_address=row2.address,
                        mentee_ethnicity=row2.ethnicity,
                        status=status,
                        features=json.dumps(score_obj["features"]),
                    )
                )

    match_suggestions = pd.DataFrame(match_suggestions)
    match_suggestions = match_suggestions.sort_values(by="score", ascending=False)
    match_suggestions = match_suggestions.reset_index(drop=True)

    return match_suggestions


class DataStore:
    def __init__(self):
        self.__matches = None
        self.mentors = None
        self.mentees = None

    def set_mentors(self, df):
        self.mentors = df

    def set_mentees(self, df):
        self.mentees = df

    def matches(self, recompute=False):
        if not recompute and self.__matches is not None:
            return self.__matches
        print("re-computing suggestions")
        self.__matches = generate_match_suggestions(self.mentors, self.mentees)
        return self.__matches

    def matches_to_show(
        self, status="sugggested", sort_by=None, filter_key=None, filter_value=None
    ):
        df = self.matches()
        df = df[df.status == status]
        rows = [r for _, r in df.iterrows()]
        feature_list = [json.loads(r.features) for r in rows]
        df["distance"] = [f.get("distance_in_miles", 1000) for f in feature_list]
        df["ethnicity_match"] = [f.get("ethnicity_match", -1) for f in feature_list]
        if (
            filter_key is not None
            and filter_key != "none"
            and filter_value is not None
            and len(str(filter_value)) > 0
        ):
            if filter_key == "distance":
                try:
                    max_distance = float(filter_value)
                except:
                    max_distance = 1000
                df = df[df["distance"].astype(float) < max_distance]
            elif filter_key=="ethnicity_match":
                df = df[df["ethnicity_match"].astype(int)==1]
            elif filter_key=="score":
                df = df[df["score"].astype(str)>=str(filter_value)]
            else:
                df = df[df[filter_key].astype(str) == str(filter_value)].reset_index(
                    drop=True
                )
        if sort_by is not None:
            df = df.sort_values(by=sort_by).reset_index(drop=True)
        return df

    def confirm_match(self, mentor_id, mentee_id):
        df = self.matches()
        rows = [r for _, r in df.iterrows()]
        for row in rows:
            if row.mentor_id == mentor_id and row.mentee_id == mentee_id:
                row["status"] = "confirmed"
        self.__matches = pd.DataFrame(rows)

    def unconfirm_match(self, mentor_id, mentee_id):
        pass

    def reject_match(self, mentor_id, mentee_id):
        df = self.matches()
        rows = [r for _, r in df.iterrows()]
        for row in rows:
            if row.mentor_id == mentor_id and row.mentee_id == mentee_id:
                row["status"] = "rejected"
        self.__matches = pd.DataFrame(rows)

    @property
    def mock_mentors(self):
        return load_mock_mentors()

    @property
    def mock_mentees(self):
        return load_mock_mentees()


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
