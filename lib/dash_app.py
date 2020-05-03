from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask

server = Flask(__name__)
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",  # for busy spin, https://community.plot.ly/t/mega-dash-loading-states/5687
]
external_scripts = [
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
]


app = Dash(
    server=server, url_base_pathname="/", external_stylesheets=external_stylesheets
)
app.config["suppress_callback_exceptions"] = True

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)
