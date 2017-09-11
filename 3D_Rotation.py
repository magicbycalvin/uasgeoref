Python
# Calculates Rotation Matrix given euler angles.
import numpy as np
import math
#def eulerAnglesToRotationMatrix(theta) :
     
 #   R_x = np.array([[1,         0,                  0                   ],
 #                   [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
 #                   [0,         math.sin(theta[0]), math.cos(theta[0])  ]
 #                    ])
         
         
                     
 #    R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                   #  [0,                     1,      0                   ],
                   #  [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                   #  ])
                 
  #  R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                   #  [math.sin(theta[2]),    math.cos(theta[2]),     0],
                   #  [0,                     0,                      1]
                   #  ])
                     
                     
   #  R = np.dot(R_z, np.dot( R_y, R_x ))
 
  #   return R

# vectorxyz = np.array([x,y,z])
# rot_value = np.dot(vectorxyz,eulerAnglesToRotationMatrix(theta))

# defining function for 3D rotation of pixel location
#currently this will just be for calculating the topleft corner but eventually this will be used to rotate the location of every pixel
def rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw):
    # non-rotated xyz of top left corner of image
    xtlnonrot = xuas - (imwidg/2)
    ytlnonrot =  yuas + (imheig/2)
    ztlnonrot = surfel
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # yaw rotation of top left corner coordinates
    xrotz = ((xtlnonrot-xuas)  * math.cos(yaw)) - ((ytlnonrot-yuas) *math.sin(yaw))+xuas
    yrotz = ((xtlnonrot-xuas)*math.sin(yaw))+((ytlnonrot-yuas)*math.cos(yaw))+yuas
    zrotz = ztlnonrot
    # roll rotation of top left corner coordinates
    xrotzx = xrotz
    yrotzx = ((yrotz-yuas)*math.cos(roll))-((zrotz-zuas)*math.sin(roll))+yuas
    zrotzx = ((yrotz-yuas)*math.sin(roll))-((zrotz-zuas)*math.cos(roll))+zuas
    # pitch rotation of top left corner coordinates
    xrotzxy = ((zrotzx-zuas)*math.sin(pitch))-((xrotzx-xuas)*math.cos(pitch))+xuas
    yrotzxy = yrotzx
    zrotzxy = ((zrotzx-zuas)*math.cos(pitch))-((xrotzx-xuas)*math.sin(pitch))+zuas

    return xrotzxy, yrotzxy, zrotzxy, xrotz, yrotz, zrotz


#eventually this will loop through each image
#info from image EXIF
# roll pitch and yaw measurements from UAS
r = 11.244716
p = -10.242028
y = 82.727883
#converting from clockwise to counterclockwise rotation
if r > 0:
    rolldeg = 360 - r
elif r <= 0:
    rolldeg = abs(r)
if p > 0:
    pitchdeg = 360 - p
elif p <= 0:
    pitchdeg = abs(p)
if y > 0:
    yawdeg = 360 - y
elif y <= 0:
    yawdeg = abs(y)

#converting roll pitch and yaw to radians
roll = np.deg2rad(rolldeg)
pitch = np.deg2rad(pitchdeg)
yaw = np.deg2rad(yawdeg)

#coordinates for UAS in UTM
xuas = 824113.2228273607
yuas = 651898.4524470394
zuas = 62.190000

# Eventually I am going to figure out how to get surface elevation using a DEM
surfel = 2.19

#camera parameters
imwidp = 4928
imheip = 3264
altitude = 60
fl = 18.3
pixsizecam = 0.0048
gsd = (pixsizecam*altitude)/(fl/100)
imwidg = gsd*imwidp
imheig = gsd*imheip
#resulting rotated coordinates
xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
