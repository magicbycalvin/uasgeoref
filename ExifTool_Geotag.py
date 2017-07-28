import os
import time
# use exif tool to geotag images and assign roll pitch and yaw using .gpx files
#changing current working directory to path where python script is located
# exiftool and .ExifTool_config file should be in the same folder as the python script
path = str(os.path.dirname(os.path.abspath(__file__)))
os.chdir(path)
jpgspath = path + '\JPEGs'
gpxpath = path + '\GPXs'
originalspath = path + '\JPEGs\Originals'
donepath = path + '\GPXs\Done'
geotagpath = path + '\JPEGs\Geotagged'
date = time.strftime("%B") + time.strftime("%d%Y")
#Place GPX files in GPX folder
#Place JPGs in JPGs folder
exiftoolcmd = 'exiftool -config .ExifTool_config -geotag=28.BIN.gpx -geotag=29.BIN.gpx -geotag=30.BIN.gpx "-geotime<${DateTimeOriginal}+00:00"' + ' ' + jpgspath
#run exiftool
os.system(exiftoolcmd)
#move originals to new folder called "Originals"
os.chdir(originalspath)
os.system('mkdir ' + date)
os.chdir(donepath)
os.system('mkdir ' + date)
os.chdir(geotagpath)
os.system('mkdir ' + date)

os.chdir(originalspath + '/' + date)
movejpgscmd = 'copy ' + jpgspath + '\*.jpg_original'
os.system(movejpgscmd)
#rename originals to just .jpg
os.system('rename *.jpg_original *.jpg')
#delete originals from folder
os.chdir(jpgspath)
os.system('del *.jpg_original')
#move geotagged to new folder called "Geotagged"
os.chdir(geotagpath + '/' + date)
movejpgscmd2 = 'copy ' + jpgspath + '\*.jpg'
os.system(movejpgscmd2)
#delete geotagged from folder
os.chdir(jpgspath)
os.system('del *.jpg')
#move GPX files to "Done" folder
os.chdir(donepath + '/' + date)
movegpxcmd = 'copy ' + gpxpath + "\*.BIN.gpx"
os.system(movegpxcmd)
#delete GPX files
os.chdir(gpxpath)
os.system('del *.BIN.gpx')
