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
from flask import Flask
from flask import Flask, send_file
from dash import Dash
from dash.dependencies import Input, State, Output
import sys
from lib import recommender, db
from lib.data_utils import parse_uploaded_content


__store__ = {}
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",  # for busy spin, https://community.plot.ly/t/mega-dash-loading-states/5687
]
external_scripts = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
]
server = Flask(__name__)
matches = []


@server.route("/health")
def index():
    return "hellow world"


app = Dash(
    server=server, url_base_pathname="/", external_stylesheets=external_stylesheets
)


def uploader(id="uploader"):
    return html.Div(
        [
            dcc.Upload(
                id=id,
                children=html.Div(["Drag and Drop or ", html.A("Select a CSV File")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                # Allow multiple files to be uploaded
                multiple=False,
            )
        ],
        className="container",
    )


def mentees_data_table():
    return html.Div(
        id="mentees-table-holder",
        className="col-6",
        children=[
            html.Div(
                className="card text-center",
                children=[
                    html.Div(html.H2("Mentees"), className="card-header"),
                    html.Div(id="mentees-table", className="card-body text-center"),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {
                                    "label": "Use Mock Data",
                                    "value": "mentees-use-mock-data",
                                }
                            ],
                            value=[],
                            id="mentees-mock-checklist",
                            inputClassName="form-check-input",
                            labelClassName="form-check-label",
                        ),
                        className="form-group form-check mt-1 mb-1",
                    ),
                    uploader(id="mentees-uploader"),
                ],
            )
        ],
    )


def mentors_data_table():
    return html.Div(
        id="mentors-table-holder",
        className="col-6",
        children=[
            html.Div(
                className="text-center card",
                children=[
                    html.Div(html.H2("Mentors"), className="card-header"),
                    html.Div(id="mentors-table", className="card-body text-center"),
                    html.Div(
                        dcc.Checklist(
                            options=[
                                {
                                    "label": "Use Mock Data",
                                    "value": "mentors-use-mock-data",
                                }
                            ],
                            value=[],
                            id="mentors-mock-checklist",
                            inputClassName="form-check-input",
                            labelClassName="form-check-label",
                        ),
                        className="form-group form-check mt-1 mb-1",
                    ),
                    uploader(id="mentors-uploader"),
                ],
            )
        ],
    )


def root_layout():
    return html.Div(
        id="app",
        className="container",
        children=[
            html.Section(
                className="jumbotron text-center",
                children=[
                    html.H1(
                        "People Matcher", className="text-center jumbotron-heading"
                    ),
                ],
            ),
            html.Div(
                className="row", children=[mentees_data_table(), mentors_data_table()]
            ),
            html.Section(
                className="jumbotron",
                children=[
                    html.Div(
                        className="form text-center",
                        children=[
                            # html.Button("Suggest All Matches", id="btn-suggest"),
                            # html.Button("Get Specific Matches", id="btn-suggest-specific"),
                            # html.Button("Download CSV File", id="down-csv-file"),
                            dcc.Link(
                                "Download CSV file", href="/download", refresh=True
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Label("Sort By"),
                            dcc.Dropdown(
                                style={"textAlign": "center",},
                                options=[
                                    {"label": "Mentor Name", "value": "mentorName"},
                                    {"label": "Mentee Name", "value": "menteeName"},
                                    {"label": "Score", "value": "score"},
                                    {"label": "Distance", "value": "distance"},
                                    {"label": "Ethinicity Match", "value": "ethnicity"},
                                ],
                                id="SORTBY",
                                placeholder="Select",
                            ),
                            html.Label("Filter By"),
                            dcc.RadioItems(
                                options=[
                                    {"label": "By Mentor", "value": "mentorName"},
                                    {"label": "By Mentee", "value": "menteeName"},
                                    {"label": "By Score", "value": "score"},
                                    {"label": "Max Distance", "value": "distance"},
                                    {"label": "Ethnicity Match", "value": "ethnicity"},
                                    {"label": "None", "value": "none"},
                                ],
                                id="FILTER",
                            ),
                            html.Div(
                                children=[
                                    html.H3("Used For Filtering:"),
                                    dcc.Input(
                                        id="get-specifics",
                                        value="Enter Here",
                                        type="text",
                                    ),
                                ],
                                id="get-specifics-container",
                                className="col text-center",
                            ),
                            # dcc.Input(id='get-specifics', value='initial value', type='text'),
                            html.Div(
                                html.Button("Get Matches", id="btn-filter"),
                                className="col text-center",
                            ),
                        ]
                    ),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                children=[],
                                id="suggested-matches-sorted-container",
                                className="col text-center",
                            )
                        ],
                    ),
                    # The original downloading button I made, container
                    # html.Div(
                    #     className="row",
                    #     children=[
                    #         html.Div(
                    #             children=[],
                    #             id="dowloading-container",
                    #             className="col text-center",
                    #         )
                    #     ],
                    # ),
                ],
            ),
        ],
    )


app.layout = root_layout()

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


@app.callback(
    Output("mentees-table", "children"),
    [Input("mentees-mock-checklist", "value"), Input("mentees-uploader", "contents")],
    [State("mentees-table", "children")],
)
def update_mentees_table(value_list, file_content, existing_state):
    if "mentees-use-mock-data" in value_list:
        df = recommender.load_mock_mentees()
        __store__["mentees"] = df
        return dash_table.DataTable(
            id="mentees-data-table",
            columns=[dict(name=c, id=c) for c in df.columns.tolist()],
            data=df.to_dict("records"),
        )
    elif file_content is not None:
        try:
            df = parse_uploaded_content(file_content)
            __store__["mentees"] = df
            return dash_table.DataTable(
                id="mentees-data-table",
                columns=[dict(name=c, id=c) for c in df.columns.tolist()],
                data=df.to_dict("records"),
            )
        except:
            return html.Div(
                "Cannot understand the uploaded file.", className="text-danger"
            )


@app.callback(
    Output("mentors-table", "children"),
    [Input("mentors-mock-checklist", "value"), Input("mentors-uploader", "contents")],
    [State("mentors-table", "children")],
)
def update_mentors_table(value_list, file_content, existing_state):
    if "mentors-use-mock-data" in value_list:
        df = recommender.load_mock_mentors()
        __store__["mentors"] = df
        return dash_table.DataTable(
            id="mentors-data-table",
            columns=[dict(name=c, id=c) for c in df.columns.tolist()],
            data=df.to_dict("records"),
        )
    elif file_content is not None:
        try:
            df = parse_uploaded_content(file_content)
            __store__["mentors"] = df
            return dash_table.DataTable(
                id="mentors-data-table",
                columns=[dict(name=c, id=c) for c in df.columns.tolist()],
                data=df.to_dict("records"),
            )
        except:
            return html.Div(
                "Cannot understand the uploaded file.", className="text-danger"
            )


def suggestion_to_dash(s, index):
    return html.Div(
        id=f"suggestion-{index}",
        className="card",
        children=html.Div(
            children=[
                html.Div(
                    className="col-4",
                    children=[
                        html.H3("Mentee: " + s[2]["name"]),
                        html.Div(s[2]["address"]),
                    ],
                ),
                html.Div(
                    className="col-4",
                    children=[
                        html.Div(f"Score: {s[0]:.3f}"),
                        html.Div(f"{s[3]['distance_in_miles']:.1f} miles"),
                        html.Div(f"ethnicity match: {s[3]['ethnicity_match']}"),
                        html.Button(
                            "👍",
                            id=f"btn-suggestion-thumbup-{index}",
                            className="btn btn-sm",
                            style={"fontSize": "2rem"},
                        ),
                        html.Button(
                            "👎",
                            id=f"btn-suggestion-thumbdown-{index}",
                            className="btn btn-sm",
                            style={"fontSize": "2rem"},
                        ),
                    ],
                ),
                html.Div(
                    className="col-4",
                    children=[
                        html.H3("Mentor: " + s[1]["name"]),
                        html.Div(s[1]["address"]),
                    ],
                ),
            ],
            className="row",
        ),
    )


def create_matches():

    if "mentors" not in __store__ or "mentees" not in __store__:
        return [
            html.Div("Please upload or use mock data for both mentors and mentees.")
        ]
    match_suggestions = recommender.generate_match_suggestions(
        # TODO: using head() for debugging, need to remove it
        __store__["mentors"],  # .head(2),
        __store__["mentees"],  # .head(2),
    )
    matches = match_suggestions
    return matches


def get_matches():
    if len(matches) == 0:
        return create_matches()
    return matches


@app.callback(
    Output("get-specifics-container", "children"),
    [Input("FILTER", "value")],
    [State("get-specifics-container", "children")],
)
def get_specifics_filtering(value_in, existing_state):
    if value_in is None:
        return existing_state

    if value_in == "mentorName":
        return [
            html.H3("Enter Mentor Name:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "menteeName":
        return [
            html.H3("Enter Mentee Name:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "score":
        return [
            html.H3("Enter Minimum Score:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "distance":
        return [
            html.H3("Enter Maximum Distance:"),
            dcc.Input(id="get-specifics", value="Enter Here", type="text"),
        ]

    if value_in == "ethnicity":
        return [
            html.H3("Only Display Matches with the Same Ethnicity"),
            dcc.Input(id="get-specifics", value="Ethnicity Matches Only", type="text"),
        ]
    if value_in == "none":
        return [
            html.H3("No Filtering"),
            dcc.Input(id="get-specifics", value="None", type="text"),
        ]


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


@app.callback(
    Output("suggested-matches-sorted-container", "children"),
    [Input("btn-filter", "n_clicks")],
    [
        State("SORTBY", "value"),
        State("FILTER", "value"),
        State("get-specifics", "value"),
        State("suggested-matches-sorted-container", "children"),
    ],
)
def specific_suggested_matches(
    n_clicks, value_in_sort, value_in_filter_type, value_in_specific, existing_state
):
    if n_clicks is None or n_clicks == "":
        return existing_state

    if "mentors" not in __store__ or "mentees" not in __store__:
        return [
            html.Div(
                ["Please upload or use mock data for both mentors and mentees."],
                className="alert alert-warning alert-dismissible fade show",
            )
        ]

    final_matches = []
    if (
        value_in_filter_type is None or value_in_filter_type == "none"
    ) and value_in_sort is not None:
        final_matches = recommender.sort_by(get_matches(), value_in_sort)
    elif value_in_filter_type is not None and value_in_sort is not None:
        final_matches = recommender.sort_by(get_matches(), value_in_sort)
        final_matches = recommender.filter_by(
            final_matches, value_in_filter_type, value_in_specific
        )
    elif value_in_filter_type is not None and value_in_sort is None:
        final_matches = recommender.filter_by(
            get_matches(), value_in_filter_type, value_in_specific
        )
    elif (
        value_in_filter_type is None or value_in_filter_type == "none"
    ) and value_in_sort is None:
        final_matches = recommender.sort_by(get_matches(), "score")

    return [
        html.H2("Suggested Matches Both", className="mt-2 mb-1"),
        # html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
        html.Div([suggestion_to_dash(s, i) for i, s in enumerate(final_matches)]),
    ]


if __name__ == "__main__":
    # sanity_check()
    db.init_db()
    app.run_server(host="0.0.0.0", debug=True)
