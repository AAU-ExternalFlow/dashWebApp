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
            html.Center(
                html.Div([
                    dbc.Row([
                        dbc.Col([dbc.Button("Run initial flow simulation", id="button_simulation", className="mx-auto col-10")]),
                        dbc.Col([dbc.Button("Run paraview", id="button_paraview", className="mx-auto col-10")]),
                    ]),
                ]),
            ),
            html.Div(id="status_text"),
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
    dbc.CardBody([
        # dbc.Button("Mesh", id="button_mesh_collapse"),
        dcc.Dropdown(id='results_dropdown', options=[], placeholder="Chose an angle of attack",),
        dbc.Button("Refresh results", id="refresh_results"),
        html.Hr(),
        dbc.Tabs([
            dbc.Tab(
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row([
                            dbc.Col([
                                dcc.Markdown('''Full domain mesh'''),
                                html.Img(id="resultImage_1",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                                # html.Img(src=("/assets/mesh1.png"),style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                                html.Br(),
                                dcc.Markdown('''Mesh at the airfoil leading edge'''),
                                html.Img(id="resultImage_3",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                            ], width=6),

                            html.Hr(),

                            dbc.Col([
                                dcc.Markdown('''Mesh refinement regions around the airfoil'''),
                                html.Img(id="resultImage_2",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                                # html.Br({'margin-top': '0'}),
                                dcc.Markdown('''Mesh at the airfoil trailing edge'''),
                                # html.Img(id="resultImage_4",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                            ], width=6),
                        ]),
                    )
                ),
                label="Mesh", tab_id="tab-Mesh"
            ),

            # dbc.Button("Results", id="button_fields_collapse"),
            dbc.Tab(
                dbc.Card(
                    dbc.CardBody(
                        dbc.Row([
                            dbc.Col([
                                dcc.Markdown('''Air velocity around the airfoil.'''),
                                html.Img(id="resultImage_4",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                                # html.Br(),
                                dcc.Markdown('''Air velocity at the airfoil leading edge'''),
                                html.Img(id="resultImage_5",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto'},className="mx-auto d-block"),
                                
                                
                            ], width=6),

                            html.Hr(),

                            dbc.Col([
                                dcc.Markdown('''Pressure around the airfoil.'''),
                                html.Img(id="resultImage_6",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                                # html.Br({'margin-top': '0'}),
                                dcc.Markdown('''Pressure at the airfoil leading edge'''),
                                html.Img(id="resultImage_7",style={'max-width': '100%', 'max-height': '275px', 'width': 'auto', 'height': 'auto','marginBottom':'20px'},className="mx-auto d-block"),
                            ], width=6),
                        ]),
                    )
                ),
                label="Fields", tab_id="tab-fields"
            ),
        ]),
        ]
    )
)

tab4Content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 5!", className="card-text"),
            dcc.Dropdown(id='results_dropdown', options=[], placeholder="Chose an angle of attack",),
            dbc.Button("Refresh", id="refresh_results"),
            
            
        ]
    )
)