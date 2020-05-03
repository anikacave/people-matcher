import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, State, Output
from lib.components.uploader import uploader


def mentees_table():
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


def mentors_table():
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
