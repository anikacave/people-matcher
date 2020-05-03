# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import base64
import datetime
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash
import dash_table
from flask import Flask, send_file
from dash.dependencies import Input, State, Output
import sys
import importlib
from lib import recommender, db
from lib.pages.index import get_layout
from lib.dash_app import app, server


@server.route("/health")
def health():
    return "I am fine."


@app.callback(
    Output("page-content", "children"), [dash.dependencies.Input("url", "pathname")]
)
def handle_url_change(pathname):
    if pathname is None or pathname == "" or pathname == "/":
        return get_layout()
    else:
        page_module = importlib.import_module(pathname.replace("/", "."), "lib.pages")
        return page_module.get_layout()


# This all goes with the original downloading button that I added

# @app.callback(
#     Output("dowloading-container", "children"),
#     [Input("down-csv-file", "n_clicks")],
#     [State("dowloading-container", "children")],

# )


# def dowloading_csv(n_clicks, existing_state):
#     if n_clicks is None or n_clicks == "":
#         return existing_state

#     return [html.H3("Downloading..."),]


@server.route("/download")
def download_csv():
    return send_file(
        "downloadFile.csv",
        mimetype="text/csv",
        attachment_filename="downloadFile.csv",
        as_attachment=True,
    )
    # change the path of the file/return multiple
    # just a random test file I made downloading on click


# @app.callback(
#     Output("suggested-matches-container", "children"),
#     [Input("btn-suggest", "n_clicks")],
#     [State("suggested-matches-container", "children")],
# )
# def update_suggested_matches(n_clicks, existing_state):
#     if n_clicks is None or n_clicks == "":
#         return existing_state
#     if "mentors" not in __store__ or "mentees" not in __store__:
#         return [
#             html.Div(["Please upload or use mock data for both mentors and mentees."], className="alert alert-warning alert-dismissible fade show",)
#         ]
#     return [
#         html.H2("Suggested Matches", className="mt-3 mb-1"),
#         #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
#         html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.sort_by(get_matches(), "mentorName"))]),
#     ]


# @app.callback(
#     Output("suggested-matches-sorted-container", "children"),
#     [Input("btn-suggest-specific", "n_clicks")],
#     [State("suggested-matches-sorted-container", "children")],
# )
# def sort_suggested_matches(n_clicks, existing_state):
#     if n_clicks is None or n_clicks == "":
#         return existing_state

#     return [
#         html.H2("Suggested Matches Sorted", className="mt-2 mb-1"),
#         #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
#         html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.sort_by(get_matches(), "mentorName"))]),
#     ]

# @app.callback(
#     Output("suggested-matches-sorted-container", "children"),
#     [Input("SORTBY", "value")],
#     [State("suggested-matches-sorted-container", "children")],
# )
# def sort_suggested_matches(value_in, existing_state):
#     if value_in is None:
#         return existing_state

#     if "mentors" not in __store__ or "mentees" not in __store__:
#         return [
#             html.Div(["Please upload or use mock data for both mentors and mentees."], className="alert alert-warning alert-dismissible fade show",)
#         ]

#     return [
#         html.H2("Suggested Matches Sorted", className="mt-2 mb-1"),
#         #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
#         html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.sort_by(get_matches(), value_in))]),
#     ]


# @app.callback(
#     Output("suggested-matches-sorted-container", "children"),
#     [Input("btn-filter", "n_clicks")],
#     [State("FILTER", "value"), State("get-specifics", "value"), State("suggested-matches-sorted-container", "children")],
# )
# def filter_suggested_matches(n_clicks, value_in_filter_type, value_in_specific, existing_state):
#     if n_clicks is None or n_clicks == "":
#         return existing_state

#     if "mentors" not in __store__ or "mentees" not in __store__:
#         return [
#             html.Div(["Please upload or use mock data for both mentors and mentees."], className="alert alert-warning alert-dismissible fade show",)
#         ]

#     return [
#         html.H2("Suggested Matches Filtered", className="mt-2 mb-1"),
#         #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
#         html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.filter_by(get_matches(), value_in_filter_type,value_in_specific))]),
#     ]


if __name__ == "__main__":
    # sanity_check()
    db.init_db()
    app.run_server(host="0.0.0.0", debug=True)
