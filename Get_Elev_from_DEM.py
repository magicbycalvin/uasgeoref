from osgeo import gdal,ogr
import numpy

def map2pixel(mx,my,gt):
    """
    Convert from map to pixel coordinates.
    Only works for geotransforms with no rotation.
    """

    px = int((mx - gt[0])/gt[1]) #x pixel
    py = int((my - gt[3])/gt[5]) #y pixel

    return px,py

src_filename = 'E:\Workspace\FLIR Test 07072017\FLIR_DEM2.tif'
src_ds=gdal.Open(src_filename)
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)

#For a single XY coordinate (must be same projection as the raster)
x=-105.11266585284145
y=39.714089
px,py=map2pixel(x,y,gt)
val = rb.ReadAsArray()
groundheight = val[py,px]
