import os
import base64
import time
import sys
from dash import Dash, html, dcc, dash_table, callback_context, callback, exceptions, no_update
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from stl import mesh
import dash_bootstrap_components as dbc
import pathlib
import numpy as np
import cv2
import ast
import shutil
import psutil
import subprocess
import _thread
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
    dcc.Store(id='raw_image_store'),  
    dcc.Store(id='blur_image_store'),  
    dcc.Store(id='canny_image_store'),  
    dcc.Store(id='bitwise_image_store'),  
    dcc.Store(id='coords_store'),
    dcc.Store(id='rotated_coords_store'),
    dcc.Store(id='STL'),
    dcc.Store(id='aoa_store'),
    dcc.Store(id='test_store'),
    dcc.Interval(id='status_interval', interval=5*1000, disabled=True),  # Check OF simulation status interval 

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
                        # dbc.Button("Flip points horizontally", id="button_flip"),
                        # html.Hr(),
                        dbc.Button("Generate 3D geometry", id="button_3D"),
                        html.Hr(),
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
                        dbc.Button("Run initial flow simulation", id="button_simulation"),
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
    [Output('raw_image', 'src'),
     Output('blur_image','src'),
     Output('canny_image','src'),
     Output('bitwise_image','src'),],
    [Input('raw_image_store', 'data'),
     Input('blur_image_store', 'data'),
     Input('canny_image_store', 'data'),
     Input('bitwise_image_store', 'data'),]
)
def display_storred_images(raw_image_data, blur_image_data, canny_image_data, bitwise_image_data):
    return raw_image_data, blur_image_data, canny_image_data, bitwise_image_data


@app.callback(
    [Output('blur_image_store', 'data'),
     Output('canny_image_store', 'data'),
     Output('bitwise_image_store', 'data')],
    [Input('blur_slider', 'value'),
     Input('canny_slider', 'value'),
     Input('raw_image_store', 'data')]
)
def process_images(blur_value, canny_value, image_data):
    if image_data is not None:
        # Decode the base64 image data
        _, content_string = image_data.split(',')
        decoded_image = base64.b64decode(content_string)

        # Convert the decoded image to numpy array
        np_image = np.frombuffer(decoded_image, dtype=np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Apply Gaussian blur
        blurred_image = shape_detection.gaussian_blur(image, blur_value)

        # Apply canny
        canny_image = shape_detection.canny(blurred_image, canny_value[0], canny_value[1])

        # Apply bitwise
        bitwise_image = shape_detection.bitwise_not(canny_image)

        # Encode the images back to base64
        blurred_content_bytes = cv2.imencode('.png', blurred_image)[1].tobytes()
        blurred_image_data = 'data:image/png;base64,' + base64.b64encode(blurred_content_bytes).decode('utf-8')

        canny_content_bytes = cv2.imencode('.png', canny_image)[1].tobytes()
        canny_image_data = 'data:image/png;base64,' + base64.b64encode(canny_content_bytes).decode('utf-8')

        bitwise_content_bytes = cv2.imencode('.png', bitwise_image)[1].tobytes()
        bitwise_image_data = 'data:image/png;base64,' + base64.b64encode(bitwise_content_bytes).decode('utf-8')

        
        return blurred_image_data, canny_image_data, bitwise_image_data

    return '', '', '' # Return empty data if image_data is None

@app.callback(
    Output('coords_store', 'data'),  
    Input('button_surface_geometry', 'n_clicks'),
    State('bitwise_image_store', 'data'),
    prevent_initial_call=True
)
def generate_surface_geometry(n_clicks, bitwise_image):
    if n_clicks is not None:
        # Decode the base64 image data
        _, content_string = bitwise_image.split(',')
        decoded_image = base64.b64decode(content_string)

        # Convert the decoded image to numpy array
        np_image = np.frombuffer(decoded_image, dtype=np.uint8)
        decoded_bitwise_image = cv2.imdecode(np_image, cv2.IMREAD_GRAYSCALE)

        coords = shape_detection.get_points(decoded_bitwise_image)

        

    return coords


@app.callback(
    Output('rotated_coords_store', 'data'),
    Output('points_plot', 'figure'),
    Input('coords_store', 'data'),
    Input('rotate_coords_slider', 'value'),
    Input('button_flip', 'n_clicks'),
    State('rotated_coords_store', 'data'),
    prevent_initial_call=True
)
def update_rotated_coords(coords, rotate_value, n_clicks, rotated_coords):
    ctx = callback_context

    if not ctx.triggered:
        raise exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id']

    if 'coords_store' in triggered_id or 'rotate_coords_slider' in triggered_id:
        rotated_coords = shape_detection.rotate_points(rotate_value, coords)
    elif 'button_flip' in triggered_id:
        if n_clicks is not None:
            rotated_coords = shape_detection.flip_coords(rotated_coords)
    
    rotated_point_plot_data = {
        'x': rotated_coords[:, 0],
        'y': rotated_coords[:, 1],
        'mode': 'markers+lines',
        'type': 'scatter',
        'marker': {'color': 'black'},  
        'line': {'color': 'black', 'width':'2'}  
    }

    layout = {
        'xaxis': {'title': 'X Axis', 'scaleanchor': 'y', 'scaleratio': 1},
        'yaxis': {'title': 'Y Axis'},
        'hovermode': 'closest',
        'margin': {'t': 0, 'b': 75, 'l': 50, 'r': 0},  # Adjust top, bottom, left, right margins
        'height': '275',
        'width': '535',
        'xaxis_range': [0, 1], 
        'yaxis_range': [0, 1]  
    }

    return rotated_coords, {'data': [rotated_point_plot_data], 'layout': layout}




def stl2mesh3d(stl_mesh):
    p, q, r = stl_mesh.vectors.shape
    vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
    I = np.take(ixr, [3*k for k in range(p)])
    J = np.take(ixr, [3*k+1 for k in range(p)])
    K = np.take(ixr, [3*k+2 for k in range(p)])
    return vertices, I, J, K


@app.callback(
    Output('stl_graph', 'figure'),
    Input('button_3D', 'n_clicks'),
    State('rotated_coords_store', 'data'),
    prevent_initial_call=True
)
def load_stl(n_clicks, rotated_coords):
    if n_clicks is not None:
        STL = shape_detection.generate_STL(rotated_coords)
        STL.save(os.path.join(os.getcwd(), 'object.stl'))  # Save the mesh to the specified path
        
    time.sleep(0.7)
    # Load the STL file (replace 'AT&T-Building.stl' with your actual file)
    my_mesh = mesh.Mesh.from_file('object.stl')
    vertices, I, J, K = stl2mesh3d(my_mesh)
    x, y, z = vertices.T
    
    colorscale = [[0, '#787878'], [1, '#787878']]
    
    mesh3D = go.Mesh3d(
        x=z,
        y=x,
        z=y,
        i=I,
        j=J,
        k=K,
        flatshading=True,
        colorscale=colorscale,
        intensity=z,
        name='STL Model',
        showscale=False
    )
    
    title = "3D Visualization of airfoil"
    layout = go.Layout(
        paper_bgcolor='rgb(255,255,255)',
        title_text=title,
        title_x=0.5,
        font_color='black',
        width=1000,
        height=550,
        scene_camera=dict(eye=dict(x=-1.5, y=1.25, z=0.5)),
        scene_xaxis_visible=False,
        scene_yaxis_visible=False,
        scene_zaxis_visible=False
        
    )
    
    fig = go.Figure(data=[mesh3D], layout=layout)
    fig.data[0].update(lighting=dict(
        ambient=0.18,
        diffuse=0.8,
        fresnel=.1,
        specular=1,
        roughness=.1,
        facenormalsepsilon=0
    ))
    fig.data[0].update(lightposition=dict(x=3000, y=3000, z=10000))
    fig.update_layout(scene_aspectmode='data')

    
    return fig


@app.callback(
    Output('aoa_array', 'children'),
    Output('aoa_store','data'),
    Input('aoa_min', 'value'),
    Input('aoa_max', 'value'),
    Input('aoa_interval', 'value')
)
def generate_array(minimum, maximum, interval):
    if minimum is None or maximum is None or interval is None:
        return "Please provide values for all inputs."

    minimum = int(round(minimum))
    maximum = int(round(maximum))
    interval = int(round(interval))

    if minimum >= maximum:
        return "Minimum should be less than maximum."

    num_elements = (maximum - minimum) // interval + 1
    array = np.linspace(minimum, maximum, num_elements, dtype=int)
    array_string = "[" + ", ".join(map(str, array)) + "]"
    # return str(array)
    return str(array_string), {'data_key': 'data_value'}

# Check if allrun is a running process
def is_simulation_running(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            return True
    return False

# Run OF callback
@app.callback(
    Output('test_store','data'),
    Input('button_simulation', 'n_clicks'),
    State('aoa_array', 'children'),
    State('rotated_coords_store', 'data'),
)
# def run_loop(n_clicks, array_string, coords):
def run_loop(n_clicks, array_string, rotated_coords_data):
    # Parse the string array into a list of integers
    array_list = ast.literal_eval(array_string)

    # Delete simulation folder if already exists.
    if os.path.exists("simulation"):
        shutil.rmtree("simulation")

    for interval in array_list:
        folderName = os.path.join("simulation", str(interval)).replace("\\","/")

        shape_detection.generateSubFolder(folderName)

        aoaCoords = shape_detection.rotate_points(interval, rotated_coords_data)
        aoaSTL = shape_detection.generate_STL(aoaCoords)

        # Save rotated aoa coordinates
        np.savetxt(f"{folderName}/coordinates.xy", aoaCoords)
        
        # Save STL geometry
        aoaSTL.save(f"{folderName}/object.stl")

        # Copy templateCase
        template_case_path = os.path.join(imageProcessing_path, 'templateCase')
        destination = shutil.copytree(template_case_path, os.path.join(folderName, 'simulation')).replace("\\","/")

        # Copy object.stl to each aoa folder
        shutil.copy(folderName+'/'+'object.stl', destination+"/constant/triSurface/object.stl").replace("\\","/")

        # Run OpenFOAM
        _thread.start_new_thread(os.system, ('bash '+folderName+'/simulation/Allrun',))

        print("simulation completed")

    return n_clicks

# Check if OF simulation is still running. 
@app.callback(
    Output('status_text', 'children'),
    Input('status_interval', 'n_intervals'),
)
def check_simulation_status(n_intervals):
    if n_intervals > 0:
        if is_simulation_running("Allrun"):
            print("Running simulations...")
            return "Running simulations..."
        else:
            print("All simulations completed")
            return "All simulations completed."
    print("Waiting for simulation start...")
    return "Waiting for simulation start..."

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