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
                    html.H1("People Matcher", className="text-center jumbotron-heading"),
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
                            html.Button("Suggest All Matches", id="btn-suggest"),
                            html.Button("Get Specific Matches", id="btn-suggest-specific"),
                            
                        ],
                    ),
                    html.Div(
                        children=[
                        html.Label('Sort By'),
                            dcc.Dropdown(style={'textAlign': 'center',},
                            options=[
                                {'label': u'Mentor Name', 'value': 'mentorName'},
                                {'label': u'Mentee Name', 'value': 'menteeName'},
                                {'label': u'Distance', 'value': 'distance'},
                                {'label': u'Ethinicity Match', 'value': 'ethnicity'}
                            ],
                            id='SORTBY',
                            placeholder="Select"
                        ),
                        html.Label('Filter By'),
                        dcc.RadioItems(
                            options=[
                                {'label': 'By Name', 'value': 'Mentor'},
                                {'label': u'Max Distance', 'value': 'MaxDist'},
                                {'label': u'Gender', 'value': 'Gender'},
                                {'label': u'Choose Ethnicity', 'value': 'Ethn'}
                            ],
                            value='MTL'
                        ),
                        ]
                    
                    ),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                children=[],
                                id="suggested-matches-container",
                                className="col text-center",
                            ),
                            html.Div(
                                children=[],
                                id="suggested-matches-sorted-container",
                                className="col text-center",
                            )
                            
                        ],
                    ),
                ],
            ),
        ],
    )


app.layout = root_layout()


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
            id="suggestion-{}".format(index),
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
                            html.Button("👍", className="btn btn-sm"),
                            html.Button("👎", className="btn btn-sm"),
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
    matches=match_suggestions
    return matches

def get_matches():
    if len(matches)==0:
        return create_matches()
    return matches
    # if len(matches)==0:
        
    #     return matches
    # else:
    #     return matches



@app.callback(
    Output("suggested-matches-container", "children"),
    [Input("btn-suggest", "n_clicks")],
    [State("suggested-matches-container", "children")],
)
def update_suggested_matches(n_clicks, existing_state):
    if n_clicks is None or n_clicks == "":
        return existing_state

    return [
        html.H2("Suggested Matches", className="mt-3 mb-1"),
        #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
        html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.sort_by(get_matches(), "mentorName"))]),
    ]

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

@app.callback(
    Output("suggested-matches-sorted-container", "children"),
    [Input("SORTBY", "value")],
    [State("suggested-matches-sorted-container", "children")],
)
def sort_suggested_matches(value_in, existing_state):
    if value_in is None:
        return existing_state

    return [
        html.H2("Suggested Matches Sorted", className="mt-2 mb-1"),
        #html.Div([suggestion_to_dash(s, i) for i, s in enumerate(sorted(matches, key=lambda s: s[2]["name"]))])
        html.Div([suggestion_to_dash(s, i) for i, s in enumerate(recommender.sort_by(get_matches(), value_in))]),
    ]


if __name__ == "__main__":
    # sanity_check()
    db.init_db()
    app.run_server(host="0.0.0.0", debug=True)

