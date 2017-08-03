#This program generates world files and projection files for viewing individual UAS photos (.JPEG) with GIS programs in the generally
#correct location/orientation.

#This program only works for nadir UAS images with square pixels.
#This program will only work for photos taken within North America - see map here: https://dds.cr.usgs.gov/srtm/version2_1/Documentation/Continent_def.gif
#unless a DEM for the area (in the form of a geotiff, such as that produced from PhotoScan) is placed in the directory \DEM\Other
#or an strm .hgt for the region is placed in the directory \DEM\STRM3.
#Camera and drone must be time-synced before the UAS flight otherwise the photos may be improperly geotagged.

#To use this program place your non-geotagged or previously geotagged images in the directory \Images\PutImagesHere.
#Get your corresponding dataflash log files (.BIN) off of the aircraft, convert put your .BIN files to .BIN.gpx files in Mission Planner.
#Place your .BIN.gpx files in the directory \GPXs.
#If you already have geotagged your images previously, the previous step is not neccessary.
#Run the code uasgeoref.py and a new folder will be generated for your original photos: \Images\Originals\date, geotagged photos: \Images\Geotagged\date,
#gpx files: \GPX\Done\date, jpgw files: \World_Files\date, prj files \PRJs\date, aux.xml files \AUXXMLs\date.
#Copy the jpgw, prj, aux.xml and geotagged jpgs into a single folder outside of this program.

#Any questions in regards to this program please email: kmason@usgs.gov or uas.usgs.gov


from math import pi, sin, cos, tan, sqrt
import numpy as np
import math
from decimal import *
from PIL import ImageTk, Image
import os
import geomag
from math import pi, sin, cos, tan, sqrt
import os
import time
import utm
from osgeo import gdal,ogr
import json


#LatLong- UTM conversion..h
#definitions for lat/long to UTM and UTM to lat/lng conversions
#include <string.h>

_deg2rad = pi / 180.0
_rad2deg = 180.0 / pi

_EquatorialRadius = 2
_eccentricitySquared = 3

_ellipsoid = [
#  id, Ellipsoid name, Equatorial Radius, square of eccentricity
# first once is a placeholder only, To allow array indices to match id numbers
[ -1, "Placeholder", 0, 0],
[ 1, "Airy", 6377563, 0.00667054],
[ 2, "Australian National", 6378160, 0.006694542],
[ 3, "Bessel 1841", 6377397, 0.006674372],
[ 4, "Bessel 1841 (Nambia] ", 6377484, 0.006674372],
[ 5, "Clarke 1866", 6378206, 0.006768658],
[ 6, "Clarke 1880", 6378249, 0.006803511],
[ 7, "Everest", 6377276, 0.006637847],
[ 8, "Fischer 1960 (Mercury] ", 6378166, 0.006693422],
[ 9, "Fischer 1968", 6378150, 0.006693422],
[ 10, "GRS 1967", 6378160, 0.006694605],
[ 11, "GRS 1980", 6378137, 0.00669438],
[ 12, "Helmert 1906", 6378200, 0.006693422],
[ 13, "Hough", 6378270, 0.00672267],
[ 14, "International", 6378388, 0.00672267],
[ 15, "Krassovsky", 6378245, 0.006693422],
[ 16, "Modified Airy", 6377340, 0.00667054],
[ 17, "Modified Everest", 6377304, 0.006637847],
[ 18, "Modified Fischer 1960", 6378155, 0.006693422],
[ 19, "South American 1969", 6378160, 0.006694542],
[ 20, "WGS 60", 6378165, 0.006693422],
[ 21, "WGS 66", 6378145, 0.006694542],
[ 22, "WGS-72", 6378135, 0.006694318],
[ 23, "WGS-84", 6378137, 0.00669438]
    ]

#Reference ellipsoids derived from Peter H. Dana's website-
#http://www.utexas.edu/depts/grg/gcraft/notes/datum/elist.html
#Department of Geography, University of Texas at Austin
#Internet: pdana@mail.utexas.edu
#3/22/95

#Source
#Defense Mapping Agency. 1987b. DMA Technical Report: Supplement to Department of Defense World Geodetic System
#1984 Technical Report. Part I and II. Washington, DC: Defense Mapping Agency

#def LLtoUTM(int ReferenceEllipsoid, const double Lat, const double Long,
#double &UTMNorthing, double &UTMEasting, char* UTMZone)

#convert lat long to UTM
#code from http://robotics.ai.uiuc.edu/~hyoon24/LatLongUTMconversion.py

def LLtoUTM(ReferenceEllipsoid, Lat, Long):
    #converts lat/long to UTM coords.  Equations from USGS Bulletin 1532
    #East Longitudes are positive, West longitudes are negative.
    #North latitudes are positive, South latitudes are negative
    #Lat and Long are in decimal degrees
    #Written by Chuck Gantz- chuck.gantz@globalstar.com

    a = _ellipsoid[ReferenceEllipsoid][_EquatorialRadius]
    eccSquared = _ellipsoid[ReferenceEllipsoid][_eccentricitySquared]
    k0 = 0.9996

    #Make sure the longitude is between -180.00 .. 179.9
    LongTemp = (Long+180)-int((Long+180)/360)*360-180 # -180.00 .. 179.9

    LatRad = Lat*_deg2rad
    LongRad = LongTemp*_deg2rad

    ZoneNumber = int((LongTemp + 180)/6) + 1

    if Lat >= 56.0 and Lat < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0:
        ZoneNumber = 32

        # Special zones for Svalbard
    if Lat >= 72.0 and Lat < 84.0:
        if  LongTemp >= 0.0  and LongTemp <  9.0:ZoneNumber = 31
        elif LongTemp >= 9.0  and LongTemp < 21.0: ZoneNumber = 33
        elif LongTemp >= 21.0 and LongTemp < 33.0: ZoneNumber = 35
        elif LongTemp >= 33.0 and LongTemp < 42.0: ZoneNumber = 37

    LongOrigin = (ZoneNumber - 1)*6 - 180 + 3 #+3 puts origin in middle of zone
    LongOriginRad = LongOrigin * _deg2rad

        #compute the UTM Zone from the latitude and longitude
    UTMZone = "%d%c" % (ZoneNumber, _UTMLetterDesignator(Lat))

    eccPrimeSquared = (eccSquared)/(1-eccSquared)
    N = a/sqrt(1-eccSquared*sin(LatRad)*sin(LatRad))
    T = tan(LatRad)*tan(LatRad)
    C = eccPrimeSquared*cos(LatRad)*cos(LatRad)
    A = cos(LatRad)*(LongRad-LongOriginRad)

    M = a*((1- eccSquared/4- 3*eccSquared*eccSquared/64- 5*eccSquared*eccSquared*eccSquared/256)*LatRad - (3*eccSquared/8+ 3*eccSquared*eccSquared/32+ 45*eccSquared*eccSquared*eccSquared/1024)*sin(2*LatRad) + (15*eccSquared*eccSquared/256 + 45*eccSquared*eccSquared*eccSquared/1024)*sin(4*LatRad) - (35*eccSquared*eccSquared*eccSquared/3072)*sin(6*LatRad))

    UTMEasting = (k0*N*(A+(1-T+C)*A*A*A/6 + (5-18*T+T*T+72*C-58*eccPrimeSquared)*A*A*A*A*A/120)+ 500000.0)

    UTMNorthing = (k0*(M+N*tan(LatRad)*(A*A/2+(5-T+9*C+4*C*C)*A*A*A*A/24 + (61 -58*T +T*T +600*C -330*eccPrimeSquared)*A*A*A*A*A*A/720)))

    if Lat < 0:
        UTMNorthing = UTMNorthing + 10000000.0; #10000000 meter offset for southern hemisphere
    return (UTMZone, UTMEasting, UTMNorthing)


def _UTMLetterDesignator(Lat):
    #This routine determines the correct UTM letter designator for the given latitude
    #returns 'Z' if latitude is outside the UTM limits of 84N to 80S
    #Written by Chuck Gantz- chuck.gantz@globalstar.com

    if  Lat >= 0: return 'N'
    elif Lat < 0: return 'S'
    else: return 'Z'	# if the Latitude is outside the UTM limits

# where code is located
path = str(os.path.dirname(os.path.abspath(__file__)))
#path names for saving and moving files
date = time.strftime("%B") + time.strftime("%d%Y")
name = date
num = 1
originalspath = os.path.join(path, 'Images\Originals')
while os.path.exists(originalspath + '/' + name):
    name = name.split('_')
    name = str(name[0]) + '_' + str(num)
    num = num + 1
DEM_path = os.path.join(path,'DEM\STRM3')
file_path = os.path.join(path,'Images\PutImagesHere')
originals = os.path.join(path, 'Images\Originals',name)
geotagged = os.path.join(path,'Images\Geotagged',name)
geotaggedpath = os.path.join(path,'Images\Geotagged')
gpxpath = os.path.join(path, 'GPXs')
gpxdone = os.path.join(gpxpath,'Done',name)
gpxdonepath = os.path.join(gpxpath,'Done')
jpwpath = os.path.join(path, 'JPGWs')
save_path_jpw = os.path.join(path,'JPGWs', name)
prjpath = os.path.join(path, 'PRJs')
save_path_prj = os.path.join(path,'PRJs', name)
auxpath = os.path.join(path, 'AUXXMLs')
save_path_aux = os.path.join(path,'AUXXMLs', name)

#creating folders
os.chdir(originalspath)
os.system('mkdir ' + name)
os.chdir(gpxdonepath)
os.system('mkdir ' + name)
os.chdir(geotaggedpath)
os.system('mkdir ' + name)
os.chdir(jpwpath)
os.system('mkdir ' + name)
os.chdir(prjpath)
os.system('mkdir ' + name)
os.chdir(auxpath)
os.system('mkdir ' + name)

#exif tool command
#change current directory to location of exif tool
os.chdir(path)
geotagcmd = 'exiftool -config .ExifTool_config -geotag "GPXs\*.BIN.gpx" "-geotime<${DateTimeOriginal}+00:00" Images\PutImagesHere'
#run exiftool command
os.system(geotagcmd)
#remove orientation tag
remorient = 'exiftool -Orientation= Images\PutImagesHere\*.JPG'
os.system(remorient)

#move originals to originals folder
os.chdir(originals)
movejpgscmd = 'copy ' + file_path + '\*.jpg_original'
os.system(movejpgscmd)
#rename originals to just .jpg
os.system('rename *.jpg_original *.jpg')
#delete originals from folder
os.chdir(file_path)
os.system('del *.jpg_original')
# move geotagged to geotagged folder
os.chdir(geotagged)
movejpgscmd2 = 'copy ' + file_path + '\*.JPG'
os.system(movejpgscmd2)
#delete geotagged photos from folder
os.chdir(file_path)
os.system('del *.jpg')
# move gpxs
os.chdir(gpxdone)
movegpxcmd = 'copy ' + gpxpath + '\*.BIN.gpx'
os.system(movegpxcmd)
# delete gpxs
os.chdir(gpxpath)
os.system('del *.BIN.gpx')

def take():
    import exifread
    import exiftool
    import os
    def get_elevation(lon, lat):
        hgt_file = get_file_name(lon, lat)
        if hgt_file:
            return read_elevation_from_file(hgt_file, lon, lat)
        # Treat it as data void as in SRTM documentation
        # if file is absent
        return -32768

    def read_elevation_from_file(hgt_file, lon, lat):
        with open(hgt_file, 'rb') as hgt_data:
            # HGT is 16bit signed integer(i2) - big endian(>)
            elevations = np.fromfile(hgt_data, np.dtype('>i2'), -1).reshape((1201, 1201))
            #elevations = np.fromfile(hgt_data, np.dtype('>i2'), SAMPLES*SAMPLES)\
                                    #.reshape((SAMPLES, SAMPLES))

            loncol = int(round(((math.ceil(abs(lon))) - abs(lon))*(1201-1)))
            latrow = int(round(((math.ceil(abs(lat)))-abs(lat))*(1201-1)))
            #lat_row = int(round((lat - int(lat)) * (SAMPLES - 1), 0))
            #lon_row = int(round((lon - int(lon)) * (SAMPLES - 1), 0))

            return elevations[latrow,loncol].astype(float)

    def get_file_name(lon, lat):

        if lat >= 0:
            ns = 'N'
        elif lat < 0:
            ns = 'S'

        if lon >= 0:
            ew = 'E'
        elif lon < 0:
            ew = 'W'

        namelat = str(int(math.floor(abs(lat))))

        if int(math.ceil(abs(lon))) >= 100:
            namelon = str(int(math.ceil(abs(lon))))
        elif int(math.ceil(abs(lon))) <100:
            namelon = str(0) + str(int(math.ceil(abs(lon))))

        hgt_file = ns + namelat+ ew + namelon+'.hgt'
        hgt_file_path = os.path.join(DEM_path, hgt_file)
        if os.path.isfile(hgt_file_path):
            return hgt_file_path
        else:
            return None


    for filename in os.listdir(geotagged):
        name = filename
        os.chdir(geotagged)
        f = open(filename,'rb')
        tags = exifread.process_file(f, details=False)
        imwidp1 = tags['EXIF ExifImageWidth']
        imwidp2 = str(imwidp1)
        im_wid_p = float(imwidp2)

        imheip1 = tags['EXIF ExifImageLength']
        imheip2 = str(imheip1)
        im_hei_p = float(imheip2)

        fl1 = tags['EXIF FocalLength']
        fl2 = repr(fl1)
        fl3 = fl2.split('=')
        fl4 = fl3[1]
        fl5 = fl4.split('/')
        focal_length = float(fl5[0])/10

        f1 = tags['EXIF FocalLengthIn35mmFilm']
        f2 = str(f1)
        f3 = float(f2)

        pix_size_cam = f3/(math.sqrt((im_wid_p**2)+(im_hei_p**2)))

        # retrieving latitude info from EXIF, converting to dec degrees
        if not 'GPS GPSLatitude' in tags:
            lat_cent = 'x'
            print filename + ' has no Latitude information!'
        else:
            lat_cent1 = str(tags['GPS GPSLatitude'])
            lat_cent2 = lat_cent1.split('[')
            lat_cent3 = lat_cent2[1]
            lat_cent4 = lat_cent3.split(']')
            lat_cent5 = lat_cent4[0]
            lat_cent6 = lat_cent5.split(',')
            lat_cent_deg = float(lat_cent6[0])
            lat_cent_min = float(lat_cent6[1])
            lat_cent_sec1 = lat_cent6[2]
            lat_cent_sec2 = lat_cent_sec1.split('/')
            lat_cent_sec = float(lat_cent_sec2[0])/ float(lat_cent_sec2[1])
            lat_sign = str(tags['GPS GPSLatitudeRef'])
            if lat_sign == 'S':
                lat_cent = float(-1) * (lat_cent_deg + ((lat_cent_min + (lat_cent_sec/float(60)))/float(60)))
            elif lat_sign == 'N':
                lat_cent = lat_cent_deg + ((lat_cent_min + (lat_cent_sec/float(60)))/float(60))

        # retrieving longitude info from EXIF,converting to dec degrees
        if not 'GPS GPSLongitude' in tags:
            long_cent = 'x'
            print filename + ' has no Longitude information!'
        else:
            long_cent1 = str(tags['GPS GPSLongitude'])
            long_cent2 = long_cent1.split('[')
            long_cent3 = long_cent2[1]
            long_cent4 = long_cent3.split(']')
            long_cent5 = long_cent4[0]
            long_cent6 = long_cent5.split(',')
            long_cent_deg = float(long_cent6[0])
            long_cent_min = float(long_cent6[1])
            long_cent_sec1 = long_cent6[2]
            long_cent_sec2 = long_cent_sec1.split('/')
            long_cent_sec = float(long_cent_sec2[0])/ float(long_cent_sec2[1])
            long_sign = str(tags['GPS GPSLongitudeRef'])
            if long_sign == 'W':
                long_cent = float(-1) * (long_cent_deg + ((long_cent_min + (long_cent_sec/float(60)))/float(60)))
            elif long_sign == 'E' :
                long_cent = long_cent_deg + ((long_cent_min + (long_cent_sec/float(60)))/float(60))

        if long_cent == 'x' or lat_cent == 'x':
            magdec = 'x'
        else:
            magdec = geomag.declination(lat_cent, long_cent)
        #magnetic declination
        if long_cent == 'x' or lat_cent == 'x':
            groundheight = 'x'
        else:
            groundheight = get_elevation(long_cent, lat_cent)

        #calculating zvalue
        if not 'GPS GPSAltitude' in tags:
            zvalue = 'x'
            print filename + 'has no altitude information'
        else:
            z1 = str(tags['GPS GPSAltitude']).split('/')
            lenz = len(z1)
            if lenz == 2:
                zvalue = float(z1[0])/float(z1[1])
            else:
                zvalue = float(z1[0])

        #calculating AGL
        if groundheight == -32768 or groundheight == -32767.0 or groundheight == 'x' or zvalue == 'x':
            AGL = 'x'
            print 'No elevation info exists for the location of ' + filename
        else:
            AGL = zvalue - groundheight

        # retrieving orientation info
        if not 'GPS GPSImgDirection' in tags:
            yaw = 'x'
            print filename + ' has no orienation information!'
        else:
            yaw1 = str(tags['GPS GPSImgDirection'])
            yaw2 = yaw1.split('/')
            lenyaw = len(yaw2)
            if lenyaw == 2:
                yaw3 = yaw2[0]
                yaw4 =yaw2[1]
                yaw5 = float(yaw3)
                yaw6 = float(yaw4)
                if str(tags['GPS GPSImgDirectionRef']) == 'T':
                    yaw = yaw5/yaw6
                elif str(tags['GPS GPSImgDirectionRef']) == 'M':
                    yaw = (yaw5/yaw6) + float(magdec)
                else:
                    yaw = 'x'
                    print filename + 'has no orientation reference information!'
            else:
                if str(tags['GPS GPSImgDirectionRef']) == 'T':
                    yaw = float(yaw2[0])
                elif str(tags['GPS GPSImgDirectionRef']) == 'M':
                    yaw = float(yaw2[0]) + float(magdec)
                else:
                    yaw = 'x'
                    print filename + 'has no orientation reference information!'

        #looping through images and generating .jpw, .prj and .aux.xml files for each image
        #first determine if proper spatial information exists
        if lat_cent == 'x' or long_cent == 'x' or yaw == 'x' or AGL == 'x':
            print 'Files will not be generated for ' + filename
        else:
            utm_coords = LLtoUTM(23, lat_cent, long_cent)
            #pixel size on the ground
            pix_size_ground = (float(pix_size_cam) * float(AGL))/(float(focal_length)/float(100))
            #image width on the ground
            im_wid_g = (float(im_wid_p) * float(pix_size_ground)) / float(100)
            #image height on the ground
            im_hei_g = (float(im_hei_p) * float(pix_size_ground)) / float(100)
            #x value of the top left corner before the image is rotated
            x_nonrot = float(utm_coords[1]) - float(im_wid_g)/float(2)
            #y value of the top left corner before the image is rotated
            y_nonrot = float(utm_coords[2]) + im_hei_g/2
            #clockwise yaw of aircraft
            #counter clockwise yaw of aircraft
            cc_yaw = 360 - yaw
            cos_cc_yaw = math.cos(math.radians(cc_yaw))
            sin_cc_yaw = math.sin(math.radians(cc_yaw))
            #x value for the center location of the image
            x_cent = utm_coords[1]
            #y value for the center location of the image
            y_cent = utm_coords[2]
            #calculating values for jpw file
            #A,D,B and E are values that describe how the image should be rotated
            A = pix_size_ground / 100 * math.cos(math.radians(yaw))
            D = pix_size_ground / 100 * math.sin(math.radians(yaw)) * -1
            B = D
            E = A * -1
            #UTM coordinates for top left corner (c,f)
            C = cos_cc_yaw *(x_nonrot-x_cent)- sin_cc_yaw *(y_nonrot-y_cent)+x_cent
            F = sin_cc_yaw *(x_nonrot-x_cent)+ cos_cc_yaw *(y_nonrot-y_cent)+y_cent

            #projection and wkt codes for every UTM zone
            if utm_coords[0]=='1N':
                project = 'PROJCS["WGS_1984_UTM_Zone_1N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-177],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='2N':
                project = 'PROJCS["WGS_1984_UTM_Zone_2N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-171],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='3N':
                project = 'PROJCS["WGS_1984_UTM_Zone_3N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-165],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='4N':
                project = 'PROJCS["WGS_1984_UTM_Zone_4N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-159],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='5N':
                project = 'PROJCS["WGS_1984_UTM_Zone_5N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-153],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='6N':
                project = 'PROJCS["WGS_1984_UTM_Zone_6N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-147],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='7N':
                project = 'PROJCS["WGS_1984_UTM_Zone_7N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-141],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='8N':
                project = 'PROJCS["WGS_1984_UTM_Zone_8N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-135],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='9N':
                project = 'PROJCS["WGS_1984_UTM_Zone_9N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-129],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='10N':
                project = 'PROJCS["WGS_1984_UTM_Zone_10N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-123],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='11N':
                project = 'PROJCS["WGS_1984_UTM_Zone_11N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='12N':
                project = 'PROJCS["WGS_1984_UTM_Zone_12N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-111],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='13N':
                project = 'PROJCS["WGS_1984_UTM_Zone_13N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='14N':
                project = 'PROJCS["WGS_1984_UTM_Zone_14N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-99],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='15N':
                project = 'PROJCS["WGS_1984_UTM_Zone_15N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='16N':
                project = 'PROJCS["WGS_1984_UTM_Zone_16N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='17N':
                project = 'PROJCS["WGS_1984_UTM_Zone_17N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='18N':
                project = 'PROJCS["WGS_1984_UTM_Zone_18N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-75],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='19N':
                project = 'PROJCS["WGS_1984_UTM_Zone_19N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-69],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='20N':
                project = 'PROJCS["WGS_1984_UTM_Zone_20N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-63],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='21N':
                project = 'PROJCS["WGS_1984_UTM_Zone_21N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-57],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='22N':
                project = 'PROJCS["WGS_1984_UTM_Zone_22N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='23N':
                project = 'PROJCS["WGS_1984_UTM_Zone_23N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='24N':
                project = 'PROJCS["WGS_1984_UTM_Zone_24N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='25N':
                project = 'PROJCS["WGS_1984_UTM_Zone_25N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-33],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='26N':
                project ='PROJCS["WGS_1984_UTM_Zone_26N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-27],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='27N':
                project = 'PROJCS["WGS_1984_UTM_Zone_27N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-21],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='28N':
                project = 'PROJCS["WGS_1984_UTM_Zone_28N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='29N':
                project = 'PROJCS["WGS_1984_UTM_Zone_29N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='30N':
                project ='PROJCS["WGS_1984_UTM_Zone_30N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='31N':
                project ='PROJCS["WGS_1984_UTM_Zone_31N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='32N':
                project = 'PROJCS["WGS_1984_UTM_Zone_32N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='33N':
                project = 'PROJCS["WGS_1984_UTM_Zone_33N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='34N':
                project ='PROJCS["WGS_1984_UTM_Zone_34N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",21],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='35N':
                project ='PROJCS["WGS_1984_UTM_Zone_35N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",27],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='36N':
                project ='PROJCS["WGS_1984_UTM_Zone_36N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",33],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='37N':
                project ='PROJCS["WGS_1984_UTM_Zone_37N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='38N':
                project ='PROJCS["WGS_1984_UTM_Zone_38N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='39N':
                project ='PROJCS["WGS_1984_UTM_Zone_39N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='40N':
                project ='PROJCS["WGS_1984_UTM_Zone_40N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",57],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='41N':
                project ='PROJCS["WGS_1984_UTM_Zone_41N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",63],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='42N':
                project ='PROJCS["WGS_1984_UTM_Zone_42N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",69],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='43N':
                project ='PROJCS["WGS_1984_UTM_Zone_43N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",75],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='44N':
                project ='PROJCS["WGS_1984_UTM_Zone_44N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='45N':
                project ='PROJCS["WGS_1984_UTM_Zone_45N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='46N':
                project ='PROJCS["WGS_1984_UTM_Zone_46N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='47N':
                project ='PROJCS["WGS_1984_UTM_Zone_47N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",99],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='48N':
                project ='PROJCS["WGS_1984_UTM_Zone_48N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='49N':
                project ='PROJCS["WGS_1984_UTM_Zone_49N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",111],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='50N':
                project ='PROJCS["WGS_1984_UTM_Zone_50N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='51N':
                project ='PROJCS["WGS_1984_UTM_Zone_51N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",123],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='52N':
                project ='PROJCS["WGS_1984_UTM_Zone_52N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",129],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='53N':
                project ='PROJCS["WGS_1984_UTM_Zone_53N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",135],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='54N':
                project ='PROJCS["WGS_1984_UTM_Zone_54N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",141],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='55N':
                project ='PROJCS["WGS_1984_UTM_Zone_55N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",147],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='56N':
                project ='PROJCS["WGS_1984_UTM_Zone_56N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",153],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='57N':
                project ='PROJCS["WGS_1984_UTM_Zone_57N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",159],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='58N':
                project ='PROJCS["WGS_1984_UTM_Zone_58N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",165],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='59N':
                project ='PROJCS["WGS_1984_UTM_Zone_59N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",171],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='60N':
                project ='PROJCS["WGS_1984_UTM_Zone_60N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",177],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["Meter",1]]'
            elif utm_coords[0]=='1S':
                project ='PROJCS["WGS_1984_UTM_Zone_1S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-177],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='2S':
                project ='PROJCS["WGS_1984_UTM_Zone_2S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-171],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='3S':
                project ='PROJCS["WGS_1984_UTM_Zone_3S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-165],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='4S':
                project ='PROJCS["WGS_1984_UTM_Zone_4S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-159],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='5S':
                project ='PROJCS["WGS_1984_UTM_Zone_5S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-153],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='6S':
                project ='PROJCS["WGS_1984_UTM_Zone_6S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-147],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='7S':
                project ='PROJCS["WGS_1984_UTM_Zone_7S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-141],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='8S':
                project ='PROJCS["WGS_1984_UTM_Zone_8S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-135],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='9S':
                project = 'PROJCS["WGS_1984_UTM_Zone_9S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-129],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='10S':
                project ='PROJCS["WGS_1984_UTM_Zone_10S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-123],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='11S':
                project ='PROJCS["WGS_1984_UTM_Zone_11S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='12S':
                project ='PROJCS["WGS_1984_UTM_Zone_12S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-111],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='13S':
                project ='PROJCS["WGS_1984_UTM_Zone_13S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='14S':
                project ='PROJCS["WGS_1984_UTM_Zone_14S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-99],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='15S':
                project ='PROJCS["WGS_1984_UTM_Zone_15S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='16S':
                project ='PROJCS["WGS_1984_UTM_Zone_16S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='17S':
                project ='PROJCS["WGS_1984_UTM_Zone_17S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='18S':
                project ='PROJCS["WGS_1984_UTM_Zone_18S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-75],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='19S':
                project ='PROJCS["WGS_1984_UTM_Zone_19S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-69],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='20S':
                project ='PROJCS["WGS_1984_UTM_Zone_20S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-63],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='21S':
                project ='PROJCS["WGS_1984_UTM_Zone_21S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-57],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='22S':
                project ='PROJCS["WGS_1984_UTM_Zone_22S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='23S':
                project ='PROJCS["WGS_1984_UTM_Zone_23S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='24S':
                project ='PROJCS["WGS_1984_UTM_Zone_24S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='25S':
                project ='PROJCS["WGS_1984_UTM_Zone_25S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-33],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='26S':
                project ='PROJCS["WGS_1984_UTM_Zone_26S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-27],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='27S':
                project ='PROJCS["WGS_1984_UTM_Zone_27S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-21],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='28S':
                project ='PROJCS["WGS_1984_UTM_Zone_28S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='29S':
                project ='PROJCS["WGS_1984_UTM_Zone_29S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='30S':
                project ='PROJCS["WGS_1984_UTM_Zone_30S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='31S':
                project ='PROJCS["WGS_1984_UTM_Zone_31S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='32S':
                project ='PROJCS["WGS_1984_UTM_Zone_32S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='33S':
                project ='PROJCS["WGS_1984_UTM_Zone_33S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='34S':
                project ='PROJCS["WGS_1984_UTM_Zone_34S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",21],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='35S':
                project ='PROJCS["WGS_1984_UTM_Zone_35S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",27],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='36S':
                project ='PROJCS["WGS_1984_UTM_Zone_36S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",33],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='37S':
                project ='PROJCS["WGS_1984_UTM_Zone_37S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",39],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='38S':
                project ='PROJCS["WGS_1984_UTM_Zone_38S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",45],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='39S':
                project ='PROJCS["WGS_1984_UTM_Zone_39S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",51],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='40S':
                project ='PROJCS["WGS_1984_UTM_Zone_40S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",57],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='41S':
                project ='PROJCS["WGS_1984_UTM_Zone_41S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",63],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='42S':
                project ='PROJCS["WGS_1984_UTM_Zone_42S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",69],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='43S':
                project ='PROJCS["WGS_1984_UTM_Zone_43S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",75],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='44S':
                project ='PROJCS["WGS_1984_UTM_Zone_44S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",81],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='45S':
                project ='PROJCS["WGS_1984_UTM_Zone_45S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",87],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='46S':
                project ='PROJCS["WGS_1984_UTM_Zone_46S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",93],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='47S':
                project ='PROJCS["WGS_1984_UTM_Zone_47S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",99],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='48S':
                project ='PROJCS["WGS_1984_UTM_Zone_48S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",105],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='49S':
                project ='PROJCS["WGS_1984_UTM_Zone_49S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",111],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='50S':
                project ='PROJCS["WGS_1984_UTM_Zone_50S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",117],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='51S':
                project ='PROJCS["WGS_1984_UTM_Zone_51S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",123],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='52S':
                project ='PROJCS["WGS_1984_UTM_Zone_52S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",129],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='53S':
                project ='PROJCS["WGS_1984_UTM_Zone_53S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",135],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='54S':
                project ='PROJCS["WGS_1984_UTM_Zone_54S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",141],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='55S':
                project ='PROJCS["WGS_1984_UTM_Zone_55S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",147],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='56S':
                project ='PROJCS["WGS_1984_UTM_Zone_56S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",153],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='57S':
                project ='PROJCS["WGS_1984_UTM_Zone_57S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",159],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='58S':
                project ='PROJCS["WGS_1984_UTM_Zone_58S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",165],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='59S':
                project ='PROJCS["WGS_1984_UTM_Zone_59S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",171],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'
            elif utm_coords[0]=='60S':
                project ='PROJCS["WGS_1984_UTM_Zone_60S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",177],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",10000000],UNIT["Meter",1]]'

            aux = '<PAMDataset> <SRS>' + project + '</SRS> </PAMDataset>'

            #generating jpw files and writing them
            new_file = open(save_path_jpw+'/'+name[:-4]+'.jpgw', 'a')
            new_file.close()
            new_file2 = open(save_path_jpw+'/'+name[:-4]+'.jpgw','w')
            new_file2.write(str(A))
            new_file2.write("\n")
            new_file2.write(str(D))
            new_file2.write("\n")
            new_file2.write(str(B))
            new_file2.write("\n")
            new_file2.write(str(E))
            new_file2.write("\n")
            new_file2.write(str(C))
            new_file2.write("\n")
            new_file2.write(str(F))
            new_file2.close()
            #generating .prj files for GlobalMapper
            new_file_prj = open(save_path_prj+'/'+name[:-4]+'.prj','a')
            new_file.close()
            new_file_prj2 = open(save_path_prj+'/'+name[:-4]+'.prj','w')
            new_file_prj2.write(str(project))
            new_file_prj2.close()
            #generating .aux.xml files for ArcMap and QGIS
            new_file_aux = open(save_path_aux+'/'+name[:-4]+'.JPG.aux.xml','a')
            new_file_aux.close()
            new_file_aux2 = open(save_path_aux+'/'+name[:-4]+'.JPG.aux.xml','w')
            new_file_aux2.write(str(aux))
            new_file_aux2.close()


    return

take()
