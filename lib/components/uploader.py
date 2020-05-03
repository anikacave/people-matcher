import dash_html_components as html
import dash_core_components as dcc


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
