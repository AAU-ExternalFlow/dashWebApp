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
import numpy as np
import cv2
from app_components import *



# Get the absolute path of the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Append paths of other directories to sys.path
main_directory_path = os.path.join(current_directory, '..')  # Parent directory
imageProcessing_path = os.path.join(current_directory, '..', 'imageProcessing')
# third_directory_path = os.path.join(current_directory, '..', 'third_directory')

sys.path.append(main_directory_path)
sys.path.append(imageProcessing_path)
# sys.path.append(third_directory_path)

import shape_detection
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
    dcc.Store(id='raw_image_store'),  # Add a dcc.Store component
    dcc.Store(id='blur_image_store'),  # Add a dcc.Store component
    dcc.Store(id='canny_image_store'),  # Add a dcc.Store component

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

#image upload, can save locally if uncomment the commented section
@app.callback(
    Output('raw_image_store', 'data'),
    Input('upload-image', 'contents')
)
def upload_image(contents):
    if contents is not None:
        # # Decode the contents of the uploaded file
        # _, content_string = contents.split(',')
        # decoded = base64.b64decode(content_string)

        # # Save the image to a file within the container's file system
        # image_filename = 'raw_image.jpg'
        # image_path = os.path.join(UPLOAD_DIR, image_filename)
        # with open(image_path, 'wb') as f:
        #     f.write(decoded)
        return contents
    return None

# Show the uploaded image
@app.callback(
    Output('raw_image', 'src'),
    Input('raw_image_store', 'data')
)
def display_uploaded_image(image_data):
    if image_data is not None:
        return image_data
    return ''

# # Load button is clicked
# @app.callback(
#     [Output('hidden-output', 'children'),
#      Output('raw_image', 'src'),
#      Output('raw_image_path','data')], # Update image path in dcc.store
#     [Input('analyse-button', 'n_clicks')],
#     [State('upload-image', 'contents')],
#     prevent_initial_call=True
# )
# def analyse_image(n_clicks, contents):
#     # if contents is not None:
#     if n_clicks is not None and n_clicks > 0:
#         # Decode the contents of the uploaded file
#         _, content_string = contents.split(',')
#         decoded = base64.b64decode(content_string)

#         # Save the image to a file within the container's file system
#         image_filename = 'raw_image.jpg'
#         image_path = os.path.join(UPLOAD_DIR, image_filename)
#         with open(image_path, 'wb') as f:
#             f.write(decoded)
        
#         encoded_image = base64.b64encode(open(image_path, 'rb').read()).decode('utf-8')
#         return [], f"data:image/png;base64,{encoded_image}", image_path

#     return [], None, None

# Blur slider
@app.callback(
    [Output('blur_image_store', 'src'),
     Output('blur_image','src')], # Outputs blurred image 
    [Input('blur_slider', 'value'),
     Input('raw_image_store', 'data')], # Fetching raw_image_store from dcc.store
)
def blur_slider(value, image_data):
    if image_data is not None:
        value = max(1, value) if value % 2 == 0 else max(1, value + 1)
        # Decode the base64 image data
        _, content_string = image_data.split(',')
        decoded_image = base64.b64decode(content_string)

        # Convert the decoded image to numpy array
        np_image = np.frombuffer(decoded_image, dtype=np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Apply Gaussian blur
        blurred_image = shape_detection.gaussian_blur(image, value)

        # Encode the blurred image back to base64
        # _, blurred_content_string = cv2.imencode('.png', blurred_image)[1].tostring()
        blurred_content_bytes = cv2.imencode('.png', blurred_image)[1].tobytes()

        blurred_image_data = 'data:image/png;base64,' + base64.b64encode(blurred_content_bytes).decode('utf-8')



        # shape_detection.image_rotate(image_path, value) # Runs blur image script

        # encoded_image = base64.b64encode(open("uploads/blurred_image.png", 'rb').read()).decode('utf-8')
        # return f"data:image/png;base64,{encoded_image}"
        return blurred_image_data, blurred_image_data  # You can store the blurred image in blur_image_store as well
    return None, None


# Angle of attack checklist ###not currently in use
# @app.callback(
#     Output('output-message', 'children'),
#     [Input('checklistAOA', 'value')],
#     prevent_initial_call=True
# )
# def save_checklist(checkbox_values):
#     if checkbox_values:
#         #Save the checklist as a text file
#         filename = 'checklist.txt'
#         file_path = os.path.join(UPLOAD_DIR, filename)

#         #Sort the checklist values in the same order as the options
#         sorted_values = sorted(checkbox_values, key=lambda x: [option['value'] for option in checklist_options].index(x))

#         with open(file_path, 'w') as f:
#             f.write('\n'.join(sorted_values))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=False)