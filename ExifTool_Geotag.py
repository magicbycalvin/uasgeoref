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
geotagcmd = 'exiftool -config .ExifTool_config -geotag "GPXs\*.BIN.gpx" "-geotime<${DateTimeOriginal}+00:00" JPEGs'
#run exiftool to geotag
os.system(geotagcmd)
#remove orientation tag
remorient = 'exiftool -Orientation= JPEGs\*.JPG'
os.system(remorient)
#move originals to new folder called "Originals"
os.chdir(originalspath)
name = date
num = 1
while os.path.exists(originalspath + '/' + name):
    name = name.split('_')
    name = str(name[0]) + '_' + str(num)
    num = num + 1
os.system('mkdir ' + name)
os.chdir(donepath)
os.system('mkdir ' + name)
os.chdir(geotagpath)
os.system('mkdir ' + name)
os.chdir(originalspath + '/' + name)
movejpgscmd = 'copy ' + jpgspath + '\*.jpg_original'
os.system(movejpgscmd)
#rename originals to just .jpg
os.system('rename *.jpg_original *.jpg')
#delete originals from folder
os.chdir(jpgspath)
os.system('del *.jpg_original')
#move geotagged to new folder called "Geotagged"
os.chdir(geotagpath + '/' + name)
movejpgscmd2 = 'copy ' + jpgspath + '\*.jpg'
os.system(movejpgscmd2)
#delete geotagged from folder
os.chdir(jpgspath)
os.system('del *.jpg')
#move GPX files to "Done" folder
os.chdir(donepath + '/' + name)
movegpxcmd = 'copy ' + gpxpath + "\*.BIN.gpx"
os.system(movegpxcmd)
#delete GPX files
os.chdir(gpxpath)
os.system('del *.BIN.gpx')
