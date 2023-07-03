import os
import datetime
# import sys
from dash import Dash, html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as pu
import pandas as pd
# import dash_uploader as du
import logging  # Add this line


UPLOAD_DIRECTORY = "/app/uploads"

debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__)


server = app.server

app.layout = html.Div([
    html.Div(children=[
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-image-upload'),
    ], style={'width': '49%', 'padding': 10, 'flex': 1}),

    html.Div(children=[
        html.Button('Analyze Image', id='analyze-button', n_clicks=0),
        html.Div(id='output-image')
    ], style={'width': '49%', 'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})

def parse_contents(contents, filename, date):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents, style={'width': '100%'}),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
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
    Output('output-image', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('upload-image', 'contents'),
    prevent_initial_call=True
)
def analyze_image(n_clicks, contents):
    if contents is not None:
        #Decode the contents of the uploaded file
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        #Save the image to a file within the container's file system
        unique_filename = str(uuid.uuid4()) + '.jpg'
        image_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
        with open(image_path, 'wb') as f:
            f.write(decoded)

        print('Analysis on uploaded image:', image_path)

        #Return the image in the output div
        return html.Img(src=contents, style={'width': '100%'})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=debug)