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
    zrotz = 0
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
    # looks like it works
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # yaw rotation of top left corner coordinates
    cc_yaw = 360 - yaw
    cos_cc_yaw = math.cos(math.radians(cc_yaw))
    sin_cc_yaw = math.sin(math.radians(cc_yaw))
    xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
    yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas

    return xrotz, yrotz

def rotatepitch(pitch):
    # looks like it works
    # pitch forward is negative, causing you to look backwards more
    # pitch backwards is positive, causing you to look forwards more
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # roll rotation of top left corner coordinates
    cc_pitch = pitch
    radpitch = math.radians(cc_pitch)
    cos_cc_pitch = math.cos(radpitch)
    sin_cc_pitch = math.sin(radpitch)
    xrotx = xtlnonrot
    yrotx1 = cos_cc_pitch *(ytlnonrot-yuas)- sin_cc_pitch *(-altitude)+yuas
    zrotx = sin_cc_pitch * (ytlnonrot-yuas)- cos_cc_pitch * (-altitude)+altitude
    phi = 90 - abs(pitch)
    phirad = math.radians(phi)
    if pitch > 0:
        yrotx = yrotx1 + (zrotx/tan(phirad))
    else:
        yrotx = yrotx1 - (zrotx/tan(phirad))

    return xrotx, yrotx, zrotx

def rotateroll(roll):
    # looks like this works now
    #an aircraft rolling right is positive, causing you too look more left
    # rolling left is negative causing you to look more right
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # pitch rotation of top left corner coordinates
    cc_roll = roll
    cos_cc_roll = math.cos(math.radians(cc_roll))
    sin_cc_roll = math.sin(math.radians(cc_roll))
        #xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
        #yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas
    xroty1 = sin_cc_roll *(-altitude)+ cos_cc_roll*(xtlnonrot-xuas)+xuas
    yroty = ytlnonrot
    zroty = cos_cc_roll *(-altitude)- sin_cc_roll*(xtlnonrot-xuas)+altitude

    phi = 90 - abs(roll)
    phirad = math.radians(phi)
    if roll > 0:
        xroty = xroty1 - (zroty/tan(phirad))
    else:
        xroty = xroty1 +(zroty/tan(phirad))

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
while r >= -80:
    xyzrot = rotateroll(r)
    print xyzrot[0]
    r = r - 10

r = 0
while r >= -80:
    xyzrot = rotateroll(r)
    print xyzrot[1]
    r = r - 10

print 'changing pitch'
while p >= -80:
    xyzrot = rotatepitch(p)
    print xyzrot[0]
    p = p - 10

p = 0
while p >= -80:
    xyzrot = rotatepitch(p)
    print xyzrot[1]
    p = p - 10

print 'changing yaw'
while y >= -80:
    xyzrot = rotateyaw(y)
    y = y - 10
    print xyzrot[0]

y = 0
while y >= -80:
    xyzrot = rotateyaw(y)
    y = y - 10
    print xyzrot[1]
