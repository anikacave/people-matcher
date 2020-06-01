import dash_html_components as html

def get_layout():
    # return html.Div("Download Page!")
    # return html.A('Download csv file here', href='/download')
    return html.Div(
        id="download",
        children=[
            html.A('download csv file here', href='/download'),
        ]
    )
