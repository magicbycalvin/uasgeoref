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
def rotate3D(roll,pitch,yaw):
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

def rotateyaw(yaw):
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # yaw rotation of top left corner coordinates
    cc_yaw = 360 - yaw
    cos_cc_yaw = math.cos(math.radians(cc_yaw))
    sin_cc_yaw = math.sin(math.radians(cc_yaw))
    xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
    yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas

    return xrotz, yrotz

def rotateroll(roll):
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # roll rotation of top left corner coordinates
    cc_roll = 360 - roll
    cos_cc_roll = math.cos(math.radians(cc_roll))
    sin_cc_roll = math.sin(math.radians(cc_roll))
    xrotx = xtlnonrot
    yrotx = cos_cc_roll *(ytlnonrot-yuas)- sin_cc_roll *(ztlnonrot-zuas)+yuas
    zrotx = sin_cc_roll * (ytlnonrot-yuas)- cos_cc_roll * (ztlnonrot-zuas)+zuas

    return xrotx, yrotx, zrotx

def rotatepitch(pitch):
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # pitch rotation of top left corner coordinates
    cc_pitch = 360 - pitch
    radpitch = math.radians(cc_pitch)
    cos_cc_pitch = math.cos(radpitch)
    sin_cc_pitch = math.sin(radpitch)
        #xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
        #yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas
    xroty = sin_cc_pitch *(ztlnonrot-zuas)- cos_cc_pitch*(xtlnonrot-xuas)+xuas
    yroty = ytlnonrot
    zroty = cos_cc_pitch *(ztlnonrot-zuas)- sin_cc_pitch*(xtlnonrot-xuas)+zuas

    return xroty, yroty, zroty


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
altitude = zuas - surfel
fl = 18.3
pixsizecam = 0.0048
gsd = (pixsizecam*altitude)/(fl/100)
imwidg = (gsd*imwidp)/100
imheig = (gsd*imheip)/100
xtlnonrot = xuas - (imwidg/2)
ytlnonrot =  yuas + (imheig/2)
ztlnonrot = surfel

#resulting rotated coordinates
print 'changing roll'
while r <= 360:
    xyzrot = rotateroll(r)
    print xyzrot[0]
    r = r + 10

r = 0
while r <= 360:
    xyzrot = rotateroll(r)
    print xyzrot[1]
    r = r + 10

print 'changing pitch'
while p <= 360:
    xyzrot = rotatepitch(p)
    print xyzrot[0]
    p = p + 10

p = 0
while p <= 360:
    xyzrot = rotatepitch(p)
    print xyzrot[1]
    p = p + 10

print 'changing yaw'
while y <= 360:
    xyzrot = rotateyaw(y)
    y = y + 10
    print xyzrot[0]

y = 0
while y <= 360:
    xyzrot = rotateyaw(y)
    y = y + 10
    print xyzrot[1]
