import subprocess

pvbatch_exe= 'D:\Program Files\ParaView 5.10.0-RC1-Windows-Python3.9-msvc2017-AMD64\bin\pvpython.exe'
# Specify the path to your ParaView Python script (trace .py file)
paraview_script = r'D:\Skole\Uni\ExternalFlow\imageProcessing\Mesh1.py'

# Construct the command to run pvbatch with the script
command = [pvbatch_exe, paraview_script]

# Run the command using subprocess
subprocess.run(command)