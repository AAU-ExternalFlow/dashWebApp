from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import base64

image_path1 = 'externalFlow.jpg'
image_path2 = 'placeholder_image.png'
image_path3 = 'externalFlow.jpg'
image_path4 = 'externalFlow.jpg'

# Using base64 encoding and decoding
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


uploadImage = [
    # html.Div(children=[
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Træk og slip eller ',
                html.A('vælg fil')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'marginBottom': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-image-upload'),
        # html.Img(id="output-image-upload", style={'max-width': '100%', 'max-height': '600px', 'width': 'auto', 'height': 'auto'}),
    # ]),
]

AOA_checklist = [
    html.Div(children=[
        html.Label('checklistAOA:'),
        html.Br(),
        dcc.Checklist(
            id='checklistAOA',
            options=[
                {'label': ' 0 grader', 'value': '0d'},
                {'label': ' 5 grader', 'value': '5d'},
                {'label': ' 10 grader', 'value': '10d'} 
            ],
            value=[]
        ),
        html.Div(id='outputAOA'),
        html.Div(id='output-message')
    ]),
]

tab1Content = dbc.Card(
    dbc.CardBody(
        [
            # html.P("This is tab 1!", className="card-text"),
            html.Img(id="analysed-image", style={'max-width': '100%', 'max-height': '600px', 'width': 'auto', 'height': 'auto'}),
        ]
    )
)

tab2Content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('''Step 1: Rå billedbehandling'''),
                    html.Img(src=b64_image(image_path1),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 3: Roter vingeprofil til angivne angrebsvinkler'''),
                    html.Img(src=b64_image(image_path2),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                ], width=6),

                html.Hr(),

                dbc.Col([
                    dcc.Markdown('''Step 2: Konverter overflade til punkter i x-y koordinatsystem'''),
                    html.Img(src=b64_image(image_path3),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 4: Omdan koordinater til 3D geometri'''),
                    html.Img(src=b64_image(image_path1),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                ], width=6)
            ]),
        ]
    )
)