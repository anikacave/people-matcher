import base64
import io
import numpy as np
import pandas as pd
import re

from lib import tasks


def find_name_column(df):
    for c in df.columns:
        if re.search(r"name", c, re.I):
            return c


def find_firstname_column(df):
    for c in df.columns:
        if re.search(r"name", c, re.I) and re.search(r"(first|given)", c, re.I):
            return c


def find_lastname_column(df):
    for c in df.columns:
        if re.search(r"name", c, re.I) and re.search(r"(last|family)", c, re.I):
            return c


def find_address_column(df):
    for c in df.columns:
        if re.search(r"address", c, re.I):
            return c


def parse_uploaded_content(content, apply_geocoder=True):
    content_type, content_string = content.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    address_col = find_address_column(df)
    if address_col:
        addresses = df[address_col].unique().tolist()
    else:
        raise ValueError(
            "Cannot find an address column. Please name the address column something like: 'address'. "
        )

    # TODO: insert the uploaded content into database.

    if apply_geocoder:
        for a in addresses:
            tasks.geocode.delay(a)
    return df


def load_mock_mentors():
    return pd.DataFrame(
        [
            # TODO: 3201 Bee Caves Rd Ste 120, Austin, TX 78746 does not work.
            {
                "name": "Beth",
                "ethnicity": "1",
                "address": "3201 Bee Caves Rd, Austin, TX 78746",
            },
            {
                "name": "Joe",
                "ethnicity": "2",
                "address": "901 W Ben White Blvd, Austin, TX 78704",
            },
            {
                "name": "Tom",
                "ethnicity": "3",
                "address": "204 E Little Elm Trail, Cedar Park, TX 78613",
            },
            {
                "name": "Paul",
                "ethnicity": "1",
                "address": "1914 E 6th St, Austin, TX 78702",
            },
            {
                "name": "Alan",
                "ethnicity": "2",
                "address": "306 Inner Campus Drive, Austin, TX 78712",
            },
            {
                "name": "Alice",
                "ethnicity": "3",
                "address": "8225 Cross Park Dr, Austin, TX 78710",
            },
            {
                "name": "Mandy",
                "ethnicity": "1",
                "address": "8557 Research Blvd, Austin, TX 78758",
            },
        ]
    ).head(3)


def load_mock_mentees():
    return pd.DataFrame(
        [
            # {
            #     "name": "Cathy",
            #     "ethnicity": "1",
            #     "address": "1445 US-183 S, Leander, TX 78641",
            # },
            {
                "name": "Neo",
                "ethnicity": "2",
                "address": "9617 Anderson Mill Rd, Austin, TX 78750",
            },
            {
                "name": "Zack",
                "ethnicity": "1",
                "address": "9422 N Lamar Blvd, Austin, TX 78753",
            },
            {
                "name": "Tim",
                "ethnicity": "3",
                "address": "1024 E Anderson Ln, Austin, TX 78752",
            },
            {"name": "Randy", "address": "5516 N Lamar Blvd, Austin, TX 78751"},
            {"name": "Frank", "address": "5762 N Mopac Expy N, Austin, TX 78731"},
            {"name": "Helen", "address": "10525 W Parmer Ln, Austin, TX 78717"},
        ]
    ).head(4)
