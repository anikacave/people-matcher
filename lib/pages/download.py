import dash_html_components as html
from flask import abort, redirect, url_for
from lib.dash_app import app, server
import dash_core_components as dcc




def get_layout():
    return html.Div(
        id="download",
        children=[
        dcc.Location(id="loc", href='/')
        ]
    )
    # return html.Div("Download Page!")
    # return html.A('Download csv file here', href='/download')
    # return html.Div(
    #     id="download",
    #     children=[
    #         html.A('No matches were made. Click here to return to the main page.', href='/'),
    #     ]
    # )
    # return html.Div(
        # id="download",
        # children=[
        # # html.Meta( httpEquiv= "refresh", url="/")

        # ]
        # return
    # )

    
