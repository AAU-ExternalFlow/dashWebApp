from dash import Dash, html, dcc
from callbacks import get_callbacks
import dash_bootstrap_components as dbc
import pathlib
from app_components import *


CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
UPLOAD_DIR = CURRENT_DIR.parents[0] / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__)

server = app.server
app.layout = html.Div([
    # dcc.store used to store data from images or other data to be used later on. 
    dcc.Store(id='raw_image_store'),  
    dcc.Store(id='blur_image_store'),  
    dcc.Store(id='canny_image_store'),  
    dcc.Store(id='bitwise_image_store'),  
    dcc.Store(id='coords_store'),
    dcc.Store(id='rotated_coords_store'),
    dcc.Store(id='STL'),
    dcc.Store(id='aoa_store'),
    dcc.Store(id='OF_callback_placeholder'),
    dcc.Store(id='paraview_callback_placeholder'),

    # dcc.interval used to detect whether simulation is finished.
    dcc.Interval(
            id='status_interval',
            interval=5*1000, # in milliseconds
            n_intervals=0,
            disabled=True
        ), 

    # The layout is made using a row and coloumn technique. 
    # Total coloumn width is 12. Tabs A-C have a width of 4 and tab 1-3 have a width of 8.
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Markdown("""
                        # External Flow: Aerodynamic analysis for abritrary 2D shapes
                        By [Jakob Hærvig](https://haervig.com/) and [Victor Hvass Mølbak](https://www.linkedin.com/in/victor-hvass-m%C3%B8lbak-3318aa1b6/).
                    """)
                ], width=True)
            ], align="end"),

            html.Hr(),

            # From here tab A-C are used to create the left hand side options and buttons.
            # Generate / run buttons are directly implemented in this code, whereas the tab contents are created in app_components.py.
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            tabAContent,
                        ),
                        html.Hr(),
                        dbc.Button("1. Shape detection settings", id="button_shape_detection"),
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

                        dbc.Button("Generate airfoil coordinates", id="button_airfoil_coordinates"),# , className="mx-auto mt-3"

                        html.Center(
                                html.Div([
                                    dbc.Row([
                                        dbc.Col([dbc.Button("Flip points horizontally", id="button_flip_hor", className="mt-3 mx-auto col-10")]),
                                        dbc.Col([dbc.Button("Flip points vertically", id="button_flip_ver", className="mt-3 mx-auto col-10")]),
                                    ]),
                                ]),
                            ),

                        html.Hr(),

                        dbc.Button("2. Generate surface geometry", id="button_3D"),
                        html.Hr(),
                        dbc.Button("3. Simulation settings", id="button_simulation_settings"),
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    tabCContent,
                                )
                            ),
                            id="collapse_simulation_settings",
                            is_open=False,
                        ), 
                        html.Hr(),
                        dbc.Button("Run simulation", id="button_simulation"),
                        html.Div(id="status_text"),
                        html.Hr(),
                        dbc.Button("Run post-processing", id="button_paraview"),
                ]),

                    html.Div(id='hidden-output', style={'display': 'none'}),
                ], width=4),

                # From here the right hand side tabs are built. These are tabs 1-3.
                dbc.Col([
                    dbc.Tabs([
                        dbc.Tab(tab1Content, label="1. Shape detection", tab_id="tab-1"),
                        dbc.Tab(tab2Content, label="2. Surface geometry", tab_id="tab-2"),
                        dbc.Tab(tab3Content, label="3. Simulation", tab_id="tab-results"),
                    ],
                    id="tabs",
                    active_tab="tab-1",
                    ),   
                ], width=8),
            ], align='start'),
        ])
    )
])


# All dash callbacks are called. 
get_callbacks(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8050", debug=False)