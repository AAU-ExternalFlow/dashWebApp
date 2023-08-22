from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
import base64
import pathlib

CURRENT_DIR = pathlib.Path(__file__).parent.resolve()

image_path1 = CURRENT_DIR / 'externalFlow.jpg'
image_path2 = CURRENT_DIR / 'placeholder_image.png'
image_path3 = CURRENT_DIR / 'externalFlow.jpg'
image_path4 = CURRENT_DIR / 'externalFlow.jpg'

# Using base64 encoding and decoding
def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


tabAContent = [
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                html.A('Drag and drop (or click to browse) shape image')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-image-upload'),
        # html.Img(id="output-image-upload", style={'max-width': '100%', 'max-height': '600px', 'width': 'auto', 'height': 'auto'}),
    # ]),
]

tabBContent = [
    html.Div(children=[
        dcc.Markdown('''Step 1: Blur'''),
        dcc.Slider(1, 25, 2, id='blur_slider', value=1, marks=None,tooltip={"placement": "bottom", "always_visible": True},updatemode='drag'),
        html.Hr(),
        dcc.Markdown('''Step 2: Canny'''),
        dcc.RangeSlider(1, 300, value=[1, 300],id='canny_slider', marks=None,tooltip={"placement": "bottom", "always_visible": True},updatemode='drag')
        # html.Label('checklistAOA:'),
        # html.Br(),
        # dcc.Checklist(
        #     id='checklistAOA',
        #     options=[
        #         {'label': ' 0 grader', 'value': '0d'},
        #         {'label': ' 5 grader', 'value': '5d'},
        #         {'label': ' 10 grader', 'value': '10d'} 
        #     ],
        #     value=[]
        # ),
        # html.Div(id='outputAOA'),
        # html.Div(id='output-message')
    ]),
]

tab1Content = dbc.Card(
    dbc.CardBody(
        [
            # html.P("This is tab 1!", className="card-text"),
            dcc.Markdown('''Raw uploaded image'''),
            html.Img(id="raw_image", src='', style={'max-width': '100%', 'max-height': '600px', 'width': 'auto', 'height': 'auto'}),
        ]
    )
)


tab2Content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('''Step 1: Gaussian blur added to remove unwanted artifacts.'''),
                    html.Img(id="blur_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 3: Image inversion.'''),
                    html.Img(id="bitwise_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                ], width=6),

                html.Hr(),

                dbc.Col([
                    dcc.Markdown('''Step 2: Edge detection by canny edge detection.'''),
                    html.Img(id="canny_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 4: Surface coordinates detection.'''),
                    dcc.Graph(id="points_plot")
                    # html.Img(src=b64_image(image_path1),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                ], width=6)
            ]),
        ]
    )
)

tab3Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 3!", className="card-text"),
            
        ]
    )
)

tab4Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 4!", className="card-text"),
        ]
    )
)

tab5Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 5!", className="card-text"),
        ]
    )
)