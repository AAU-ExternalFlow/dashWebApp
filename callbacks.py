from dash import dash, callback_context, callback, exceptions
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from stl import mesh
import base64
import os
import sys
import numpy as np
import cv2
import time
import shutil
import psutil
import ast
import _thread


# Get the absolute path of the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Append paths of other directories to sys.path
main_directory_path = os.path.join(current_directory, '..')  # Parent directory
imageProcessing_path = os.path.join(current_directory, '..', 'imageProcessing')

sys.path.append(main_directory_path)
sys.path.append(imageProcessing_path)

import shape_detection
import Results
import generateSTL


def get_callbacks(app): 

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


    #Callback to expand simulation settings menu.
    @app.callback(
        Output("collapse_simulation_settings", "is_open"),
        [Input("button_simulation_settings", "n_clicks")],
        [State("collapse_simulation_settings", "is_open")]
    )
    def toggle_simulation_collapse(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open


    # Store uploaded image.
    @app.callback(
        Output('raw_image_store', 'data'),
        Input('upload-image', 'contents')
    )
    def upload_image(contents):
        if contents is not None:
            return contents
        return None


    # Show the uploaded image and output so it can be processed.
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


    # Image processing
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


    # Generate airfoil coordinates.
    @app.callback(
        Output('coords_store', 'data'),  
        Input('button_airfoil_coordinates', 'n_clicks'),
        State('bitwise_image_store', 'data'),
        prevent_initial_call=True
    )
    def generate_airfoil_coordinates(n_clicks, bitwise_image):
        if n_clicks is not None:
            # Decode the base64 image data
            _, content_string = bitwise_image.split(',')
            decoded_image = base64.b64decode(content_string)

            # Convert the decoded image to numpy array
            np_image = np.frombuffer(decoded_image, dtype=np.uint8)
            decoded_bitwise_image = cv2.imdecode(np_image, cv2.IMREAD_GRAYSCALE)

            coords = shape_detection.get_points(decoded_bitwise_image)
        return coords


    # Update airfoil coordinates if any of the rotation buttons are pressed and create plot.
    @app.callback(
        Output('rotated_coords_store', 'data'),
        Output('points_plot', 'figure'),
        Input('coords_store', 'data'),
        Input('button_flip_hor', 'n_clicks'),
        Input('button_flip_ver', 'n_clicks'),
        State('rotated_coords_store', 'data'),
        prevent_initial_call=True
    )
    def update_rotated_coords(coords, n_clicks1, n_clicks2, rotated_coords):
        ctx = callback_context

        if not ctx.triggered:
            raise exceptions.PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id']

        # If any rotations buttons are pressed perform actions:
        if 'coords_store' in triggered_id:
            rotated_coords = shape_detection.rotate_points(0, coords)
        elif 'button_flip_hor' in triggered_id:
            if n_clicks1 is not None:
                rotated_coords = shape_detection.flip_coords_hor(rotated_coords)
        elif 'button_flip_ver' in triggered_id:
            if n_clicks2 is not None:
                rotated_coords = shape_detection.flip_coords_ver(rotated_coords)
        
        # Create airfoil coordinates plot.
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


    # STL to surface points.
    def stl2mesh3d(stl_mesh):
        p, q, r = stl_mesh.vectors.shape
        vertices, ixr = np.unique(stl_mesh.vectors.reshape(p*q, r), return_inverse=True, axis=0)
        I = np.take(ixr, [3*k for k in range(p)])
        J = np.take(ixr, [3*k+1 for k in range(p)])
        K = np.take(ixr, [3*k+2 for k in range(p)])
        return vertices, I, J, K

    # Generate STL file and show interactive 3D surface plot.
    @app.callback(
        Output('stl_graph', 'figure'),
        Input('button_3D', 'n_clicks'),
        State('rotated_coords_store', 'data'),
        prevent_initial_call=True
    )
    def load_stl(n_clicks, rotated_coords):
        if n_clicks is not None:
            STL = generateSTL.generate_STL(rotated_coords)
            STL.save(os.path.join(os.getcwd(), 'object.stl'))  # Save the STL to the specified path
            
        time.sleep(0.7) # Short timer to give the STL time to save correctly.
        my_mesh = mesh.Mesh.from_file('object.stl')
        vertices, I, J, K = stl2mesh3d(my_mesh)
        x, y, z = vertices.T
        
        #Create 3D surface plot:
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


    # Generate AOA array dependend on inputs given in dash app.
    @app.callback(
        Output('aoa_array', 'children'),
        Output('aoa_store','data'),
        Output('results_dropdown', 'options'),
        Input('aoa_min', 'value'),
        Input('aoa_max', 'value'),
        Input('aoa_interval', 'value')
    )
    def generate_array(minimum, maximum, interval):
        if minimum is None or maximum is None or interval is None:
            return "Please provide values for all inputs."

        # Round off the input numbers.
        minimum = int(round(minimum))
        maximum = int(round(maximum))
        interval = int(round(interval))

        if minimum >= maximum:
            return "Minimum should be less than maximum."

        num_elements = (maximum - minimum) // interval + 1
        array = np.linspace(minimum, maximum, num_elements, dtype=int)
        array_string = "[" + ", ".join(map(str, array)) + "]"

        # Create options for the dropdown menu in results tab.
        dropdown_options = [{'label': str(val), 'value': str(val)} for val in array]

        return str(array_string), {'data_key': 'data_value'}, dropdown_options


    # Check if any OF process is a running
    def is_simulation_running(*process_names):
        for proc in psutil.process_iter(['pid', 'name']):
            if any(name in proc.info['name'] for name in process_names):
                return True
        return False


    # Run OF.
    @app.callback(
        Output('OF_callback_placeholder','data'),
        Input('button_simulation', 'n_clicks'),
        State('aoa_array', 'children'),
        State('rotated_coords_store', 'data'),
    )
    def run_loop(n_clicks, array_string, rotated_coords_data):
        # Parse the string array into a list of integers
        array_list = ast.literal_eval(array_string)

        # Delete simulation folder if it already exists.
        if os.path.exists("simulation"):
            shutil.rmtree("simulation")

        for interval in array_list:
            folderName = os.path.join("simulation", str(interval)).replace("\\","/")

            Results.generateSubFolder(folderName)

            # Create STL dependend on given AOAs.
            aoaCoords = shape_detection.rotate_points(interval, rotated_coords_data)
            aoaSTL = generateSTL.generate_STL(aoaCoords)

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
        return n_clicks


    # Paraview run picture scripts (Meshx.py, Px.py Ux.py)
    @app.callback(
        Output('paraview_callback_placeholder','data'),
        Input('button_paraview', 'n_clicks'),
        State('aoa_array', 'children')
    )
    def run_paraview(n_clicks, aoa_array):
        if n_clicks is not None:
            # Split the string representation of the array and convert to integers
            aoa_array = [int(value) for value in aoa_array[1:-1].split(', ')]

            # Create directories based on aoa_array values
            for aoa_value in aoa_array:
                directory_name = f"assets/{aoa_value}"
                os.makedirs(directory_name, exist_ok=True)  # Create directory if it does not exist

            Results.paraviewResults(aoa_array)
        return n_clicks


    # Active status_interval when simulation button is pressed.
    @app.callback(
        Output('status_interval', 'disabled'),
        Input('button_simulation', 'n_clicks'),
    )
    def toggle_interval(n_clicks):
        return n_clicks is None
    

    # Check if OF simulation is still running, every status_interval period.
    @app.callback(
        Output('status_text', 'children'),
        Input('status_interval', 'n_intervals'),
    )
    def check_simulation_status(n_intervals):
        if n_intervals > 0:
            if is_simulation_running("Allrun", "blockMesh", "snappyHexMesh", "extrudeMesh", "simpleFoam"):
                return "Running simulations..."
            else:
                return "All simulations completed."
        return "Waiting for simulation start..."


    # Generate images of mesh, velocity and pressure fields.
    @app.callback(
        [Output(f'resultImage_{i}', 'src') for i in range(1, 9)],
        Input('refresh_results', 'n_clicks'),
        State('results_dropdown', 'value')
    )
    def update_output(n_clicks, value):
        if n_clicks is not None:

            image_paths = [
                f'/externalflow/assets/{value}/mesh1.png',
                f'/externalflow/assets/{value}/mesh2.png',
                f'/externalflow/assets/{value}/mesh3.png',
                f'/externalflow/assets/{value}/mesh4.png',
                f'/externalflow/assets/{value}/U1.png',
                f'/externalflow/assets/{value}/U2.png',
                f'/externalflow/assets/{value}/P1.png',
                f'/externalflow/assets/{value}/P2.png',
            ]

            encoded_images = []
            for path in image_paths:
                if os.path.exists(path):
                    with open(path, 'rb') as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('ascii')
                        encoded_images.append(f'data:image/png;base64,{encoded_image}')
                else:
                    encoded_images.append(None)

            return encoded_images
        else:
            # If the button hasn't been clicked yet
            return [dash.no_update] * 8
        