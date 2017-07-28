import os

#changing current working directory to path where python script is located
# exiftool and .ExifTool_config file should be in the same folder as the python script
path = str(os.path.dirname(os.path.abspath(__file__)))
os.chdir('path')
os.system('exiftool -config .ExifTool_config -geotag=28.BIN.gpx -geotag=29.BIN.gpx -geotag=30.BIN.gpx "-geotime<${DateTimeOriginal}+00:00" E:\Workspace\ExifTool\Jpegs')

:: use exif tool to geotag images and assign roll pitch and yaw using .gpx files
import os
