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
        dcc.RangeSlider(1, 300, value=[1, 300],id='canny_slider', marks=None,tooltip={"placement": "bottom", "always_visible": True},updatemode='drag'),
        html.Hr(),
        html.Center(
            dbc.Button("Generate airfoil coordinates", id="button_airfoil_coordinates", className="mx-auto mt-3"),
        ),
        html.Hr(),
        html.Center(
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Button("Flip points horizontally", id="button_flip_hor", className="mx-auto col-10")]),
                    dbc.Col([dbc.Button("Flip points vertically", id="button_flip_ver", className="mx-auto col-10")]),
                    # dbc.Button("Flip points horizontally", id="button_flip_hor", className="mx-auto"),  
                    # dbc.Button("Flip points vertically", id="button_flip_ver", className="mx-auto"), 
                ]),
            ]),
        ),
    ]),
]

tabCContent = [
    html.Div(children=[
        dbc.Row([
            dbc.Col([
                dcc.Markdown('''Angles of attack inputs:'''),
                dcc.Input(id="aoa_min", type="number", placeholder="AOA minimum",style={'max-width': '100%'}),
                dcc.Input(id="aoa_max", type="number", placeholder="AOA maximum",style={'max-width': '100%'}),
                dcc.Input(id="aoa_interval", type="number", placeholder="AOA interval",style={'max-width': '100%'}),
                ], width=6),
                dbc.Col([
                dcc.Markdown('''Angles of attack to be simulated:'''),
                html.Div(id='aoa_array'),
                ], width=6),
            ]),
            html.Hr(),
            dbc.Button("Run initial flow simulation", id="button_simulation"),
            dbc.Button("Run paraview", id="button_paraview"),
            html.Div(id="status_text"),
            html.Div(id="paraview_text"),
    ]),
]

tab1Content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('''Step 1: Gaussian blur added to remove unwanted artifacts.'''),
                    html.Img(id="blur_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 3: Image inversion.'''),
                    html.Img(id="bitwise_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                    
                    # Hidden raw image. Needed to show blurred image.
                    html.Img(id="raw_image", src='', style={'display': 'none'}),
                ], width=6),

                html.Hr(),

                dbc.Col([
                    dcc.Markdown('''Step 2: Edge detection by canny edge detection.'''),
                    html.Img(id="canny_image",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br({'margin-top': '0'}),
                    dcc.Markdown('''Step 4: Airfoil surface coordinates. The front of the airfoil should be at (0, 0)'''),
                    dcc.Graph(id="points_plot",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'}),
                    # dcc.Slider(0, 360, 1, id='rotate_coords_slider', value=0, marks=None, tooltip={"placement": "bottom", "always_visible": True},updatemode='drag'),
                    
                    # html.Img(src=b64_image(image_path1),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                ], width=6)
            ]),
        ]
    )
)

tab2Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("A 3D view of your airfoil:", className="card-text"),
            dcc.Graph(id='stl_graph'),
            
        ]
    )
)

tab3Content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col([
                    dcc.Markdown('''Step 1: Gaussian blur added to remove unwanted artifacts.'''),
                    html.Img(id="resultImage_1",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    html.Br(),
                    dcc.Markdown('''Step 3: Image inversion.'''),
                    # html.Img(id="resultImage_2",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                    
                    
                ], width=6),

                html.Hr(),

                dbc.Col([
                    dcc.Markdown('''Step 2: Edge detection by canny edge detection.'''),
                    html.Img(id="resultImage_2",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                    # html.Br({'margin-top': '0'}),
                    dcc.Markdown('''Step 4: Airfoil surface coordinates. The front of the airfoil should be at (0, 0)'''),
                ], width=6)
            ]),
        ]
    )
)

tab4Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 5!", className="card-text"),
        ]
    )
)