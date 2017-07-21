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

    return xrotzxy, yrotzxy, zrotzxy


r = 0
p = 0
y = 0
#coordinates for UAS in UTM taken from Barren Ricoh
xuas = 827106.3613
yuas = 649895.2486
zuas = 131.16
# Eventually I am going to figure out how to get surface elevation using a DEM
surfel = 2.19
#camera parameters
imwidp = 4928
imheip = 3264
altitude = 131.6
fl = 18.3
pixsizecam = 0.0048
gsd = (pixsizecam*altitude)/(fl/100)
imwidg = (gsd*imwidp)/100
imheig = (gsd*imheip)/100
#resulting rotated coordinates
print 'changing roll'
while r <= 360:
    p = 0
    y = 0
    #converting roll pitch and yaw to radians
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[0]
    r = r + 10

r = 0
while r <= 360:
    p = 0
    y = 0
    #converting roll pitch and yaw to radians
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[1]
    r = r + 10

print 'changing pitch'
while p <= 360:
    r = 0
    y = 0
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[0]
    p = p + 10

p = 0
while p <= 360:
    r = 0
    y = 0
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[1]
    p = p + 10

print 'changing yaw'
while y <= 360:
    p = 0
    r = 0
    y = y + 10
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[0]

y = 0
while y <= 360:
    p = 0
    r = 0
    y = y + 10
    roll = np.deg2rad(r)
    pitch = np.deg2rad(p)
    yaw = np.deg2rad(y)
    xyzrot = rotate3D(xuas,yuas,zuas,imwidg,imheig,surfel,roll,pitch,yaw)
    print xyzrot[1]
