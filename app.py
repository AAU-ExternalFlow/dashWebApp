import os
import datetime
import base64
import uuid
import time
import sys
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as pu
import pandas as pd
import dash_bootstrap_components as dbc
import pathlib
from app_components import *
# from externalflow.imageProcessing.shape_detection.py import *


# Get the absolute path of the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Append paths of other directories to sys.path
main_directory_path = os.path.join(current_directory, '..')  # Parent directory
imageProcessing_path = os.path.join(current_directory, '..', 'imageProcessing')
# third_directory_path = os.path.join(current_directory, '..', 'third_directory')

sys.path.append(main_directory_path)
sys.path.append(imageProcessing_path)
# sys.path.append(third_directory_path)

from shape_detection.py import image_rotate as image_rotate
# from third_script import your_function as third_function



CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
UPLOAD_DIR = CURRENT_DIR.parents[0] / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

checklist_options = [
    {'label': '0degrees', 'value': '0d'},
    {'label': '5degrees', 'value': '5d'},
    {'label': '10degrees', 'value': '10d'}
]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__)

image_path = CURRENT_DIR / 'externalFlow.jpg'

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
                        # External Flow: Aerodynamic analyser for abritrary 2D shapes
                        By [Jakob Hærvig](https://haervig.com/) and [Victor Hvass Mølbak](https://www.linkedin.com/in/victor-hvass-m%C3%B8lbak-3318aa1b6/).
                    """)
                ], width=True)
            ], align="end"),

            html.Hr(),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            tabAContent,
                        ),
                        html.Hr(),
                        dbc.Button("Shape detection", id="button_shape_detection"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    tabBContent,
                                )
                            ),
                            id="collapse_shape_detection",
                            is_open=False,
                        ),
                        html.Hr(),
                        dbc.Button("Generate surface geometry", id="button_surface_geometry"),
                        html.Hr(),
                        dbc.Button("Generate mesh", id="button_mesh"),
                        html.Hr(),
                        dbc.Button("Run initial flow simulation", id="button_initial_flow_simulation"),
                ]),

                    html.Div(id='hidden-output', style={'display': 'none'}),
                ], width=4),

                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(tab1Content, label="1. Raw image Loaded", tab_id="tab-1"),
                        dbc.Tab(tab2Content, label="2. Shape detection", tab_id="tab-2"),
                        dbc.Tab(tab3Content, label="3. Surface geometry", tab_id="tab-3"),
                        dbc.Tab(tab4Content, label="4. Mesh", tab_id="tab-4"),
                        dbc.Tab(tab5Content, label="5. Initial flow simulation", tab_id="tab-5"),
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



#Callback to expand shape detection menu.
@app.callback(
    Output("collapse_shape_detection", "is_open"),
    [Input("button_shape_detection", "n_clicks")],
    [State("collapse_shape_detection", "is_open")]
)
def toggle_shape_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

def parse_contents(contents, filename, date):
    return html.Div([
        # html.H5(filename),
        #HTML images accept base64 encoded strings in the same format that is supplied by the upload
        dbc.Button("Load image", id='analyse-button', n_clicks=0),
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
        image_path = os.path.join(UPLOAD_DIR, unique_filename)
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
        rotate_newest_image(UPLOAD_DIR, 90)
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
        file_path = os.path.join(UPLOAD_DIR, filename)

        #Sort the checklist values in the same order as the options
        sorted_values = sorted(checkbox_values, key=lambda x: [option['value'] for option in checklist_options].index(x))

        with open(file_path, 'w') as f:
            f.write('\n'.join(sorted_values))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=False)