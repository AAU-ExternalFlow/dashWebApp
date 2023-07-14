import os
import datetime
import base64
import uuid
import time
# import sys
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as pu
import pandas as pd
import dash_bootstrap_components as dbc

from app_components import *
from rotate import *

UPLOAD_DIRECTORY = "/app/uploads" #

checklist_options = [
    {'label': '0degrees', 'value': '0d'},
    {'label': '5degrees', 'value': '5d'},
    {'label': '10degrees', 'value': '10d'}
]

debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'bootstrap.css'])
app = Dash(__name__)

image_path = 'externalFlow.jpg'

# Using base64 encoding and decoding
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


server = app.server
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            # html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Markdown("""
                        # [External Flow AAU Energy](https://externalflow.energy.aau.dk/)
                        By [Jakob Hærvig](https://haervig.com/) and [Victor Hvass Mølbak](https://www.linkedin.com/in/victor-hvass-m%C3%B8lbak-3318aa1b6/).
                    """)
                ], width=True),
                dbc.Col([
                    html.Img(src=b64_image(image_path), height="80px"),
                ], width=1.7)
            ], align="end"),

            html.Hr(),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            uploadImage,
                        ),
                        dbc.Button("Angrebsvinkel", id="button_AOA", style={'marginBottom':'10px', 'marginTop':'-20px', 'width':'150px', 'marginLeft':'20px'}),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    AOA_checklist,
                                )
                            ),
                            id="collapse_AOA",
                            is_open=False
                        ),
                ]),

                    html.Div(id='hidden-output', style={'display': 'none'}),
                ], width=4),

                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(tab1Content, label="Aerodynamisk analyse", tab_id="tab-1"),
                        dbc.Tab(tab2Content, label="Billedanalyse", tab_id="tab-2"),
                    ],
                    id="tabs",
                    active_tab="tab-1",
                    ),

                    # html.Img(id="analysed-image", style={'max-width': '100%', 'max-height': '600px', 'width': 'auto', 'height': 'auto'}),       
                ], width=8),
            ], align='start'),
        ])
    )
])



#Callback to expand AOA menu.
@app.callback(
    Output("collapse_AOA", "is_open"),
    [Input("button_AOA", "n_clicks")],
    [State("collapse_AOA", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open



def parse_contents(contents, filename, date):
    return html.Div([
        # html.H5(filename),
        #HTML images accept base64 encoded strings in the same format that is supplied by the upload
        html.Img(src=contents, style={'max-width': '100%', 'max-height': '475px', 'width': 'auto', 'height': 'auto','margin-bottom': '10px'}),
        dbc.Button("Analyser tegning", id='analyse-button', n_clicks=0),
        html.Hr(),

    ])

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(contents, filename, date):
    if contents is not None:
        children = [
            parse_contents(contents, filename, date)
        ]
        return children


@app.callback(
    Output('hidden-output', 'children'),
    Input('analyse-button', 'n_clicks'),
    State('upload-image', 'contents'),
    prevent_initial_call=True
)
def analyse_image(n_clicks, contents):
    # if contents is not None:
    if n_clicks is not None and n_clicks > 0:
        # Decode the contents of the uploaded file
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Save the image to a file within the container's file system
        unique_filename = str(uuid.uuid4()) + '.jpg'
        image_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        with open(image_path, 'wb') as f:
            f.write(decoded)

    return []

@app.callback(
    Output('analysed-image', 'src'),
    Input('analyse-button', 'n_clicks'),
    State('analysed-image', 'src'),
    prevent_initial_call=True
)
def analyse_image(n_clicks, contents):
    # if contents is not None:
    if n_clicks is not None and n_clicks > 0:
        time.sleep(1)
        rotate_newest_image("/app/uploads", 90)
        #Return the rotated image path or encoded image content
        rotated_image_path = "rotated_image.png"
        encoded_image = base64.b64encode(open(rotated_image_path, 'rb').read()).decode('utf-8')
        return f"data:image/png;base64,{encoded_image}"




@app.callback(
    Output('output-message', 'children'),
    [Input('checklistAOA', 'value')],
    prevent_initial_call=True
)
def save_checklist(checkbox_values):
    if checkbox_values:
        #Save the checklist as a text file
        filename = 'checklist.txt'
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)

        #Sort the checklist values in the same order as the options
        sorted_values = sorted(checkbox_values, key=lambda x: [option['value'] for option in checklist_options].index(x))

        with open(file_path, 'w') as f:
            f.write('\n'.join(sorted_values))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=debug)