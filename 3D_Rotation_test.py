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




def rotateyaw(xtlnonrot,xuas, ytlnonrot, yuas, yaw):
    # looks like it works
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # yaw rotation of top left corner coordinates
    cc_yaw = 360 - yaw
    cos_cc_yaw = math.cos(math.radians(cc_yaw))
    sin_cc_yaw = math.sin(math.radians(cc_yaw))
    xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
    yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas

    return xrotz, yrotz

def rotatepitch(xtlnonrot,xuas, ytlnonrot, yuas, altitude, pitch):
    # looks like it works
    # pitch forward is negative, causing you to look backwards more
    # pitch backwards is positive, causing you to look forwards more
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # roll rotation of top left corner coordinates
    cc_pitch = abs(pitch)
    radpitch = math.radians(cc_pitch)
    cos_cc_pitch = math.cos(radpitch)
    sin_cc_pitch = math.sin(radpitch)

    xrotx = xtlnonrot
    if pitch < 0:
        yrotx2 = (cos_cc_pitch *(ytlnonrot-yuas)- sin_cc_pitch *(-altitude)) + yuas
        yrotx1 = ytlnonrot - (yrotx2 - ytlnonrot)
        zrotx = sin_cc_pitch * (ytlnonrot-yuas)- cos_cc_pitch * (-altitude)+altitude
    else:
        #xroty1 = (sin_cc_roll *(-altitude)+ cos_cc_roll*(xtlnonrot-xuas))+xuas
        yrotx1 = (cos_cc_pitch *(ytlnonrot-yuas)- sin_cc_pitch *(-altitude))+yuas
        zrotx = sin_cc_pitch * (ytlnonrot-yuas)- cos_cc_pitch * (-altitude)+altitude

    phipitch = 90 - abs(pitch)
    phiradpitch = math.radians(phipitch)
    if pitch > 0:
        yrotx = yrotx1 + (zrotx/math.tan(phiradpitch))
    else:
        yrotx = yrotx1 - (zrotx/math.tan(phiradpitch))

    return xrotx, yrotx, zrotx

def rotateroll(xtlnonrot,xuas, ytlnonrot, yuas, altitude, roll):
    # looks like this works now
    #an aircraft rolling right is positive, causing you too look more left
    # rolling left is negative causing you to look more right
    # need to rotate points about the center of the drone, so pretend drone location is (0,0,0)
    # pitch rotation of top left corner coordinates
    cc_roll = abs(roll)
    cos_cc_roll = math.cos(math.radians(cc_roll))
    sin_cc_roll = math.sin(math.radians(cc_roll))
        #xrotz  = cos_cc_yaw *(xtlnonrot-xuas)- sin_cc_yaw *(ytlnonrot-yuas)+xuas
        #yrotz = sin_cc_yaw *(xtlnonrot-xuas)+ cos_cc_yaw *(ytlnonrot-yuas)+yuas
    if roll <0:
        xroty2 = sin_cc_roll *(-altitude)+ cos_cc_roll*(xtlnonrot-xuas)+xuas
        xroty1 = xtlnonrot + (xtlnonrot - xroty2)
        yroty = ytlnonrot
        zroty = cos_cc_roll *(-altitude)- sin_cc_roll*(xtlnonrot-xuas)+altitude
    else:
        xroty1 = (sin_cc_roll *(-altitude)+ cos_cc_roll*(xtlnonrot-xuas))+xuas
        yroty = ytlnonrot
        zroty = cos_cc_roll *(-altitude)- sin_cc_roll*(xtlnonrot-xuas)+altitude

    phi = 90 - abs(roll)
    phirad = math.radians(phi)
    if roll > 0:
        xroty = xroty1 - (zroty/math.tan(phirad))
    else:
        xroty = xroty1 +(zroty/math.tan(phirad))

    return xroty, yroty, zroty

# defining function for 3D rotation of pixel location
def rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, roll,pitch,yaw):
    rotx = rotatepitch(xtlnonrot,xuas,  ytlnonrot, yuas, altitude, pitch)
    rotxy = rotateroll(rotx[0], xuas, rotx[1], yuas, altitude, roll)
    rotxyz = rotateyaw(rotxy[0], xuas, rotxy[1], yuas, yaw)

    return rotxyz[0], rotxyz[1]


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
r = 50
p = 50
y = 50
x = []
y1 = []
roll1 = []
yaw7 = []
pitch1 = []
print 'Changing roll pitch and yaw'
while r >= -50:
    p = 50
    y = 50
    while p >= -50:
        y = 50
        while y >= -50:
            xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, r,p,y)
            x.append(xyzrot[0])
            y1.append(xyzrot[1])
            roll1.append(r)
            yaw7.append(y)
            pitch1.append(p)
            y = y -10
        xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, r,p,y)
        p = p - 10
    xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, r,p,y)
    r = r - 10


r = 50
p = 50
y = 50

new_file = open('E:\Workspace\Georeferencing UAS Photos' +'/'+'rollpitchyaw.txt', 'a')
new_file.close()
new_file2 = open('E:\Workspace\Georeferencing UAS Photos' +'/'+'rollpitchyaw.txt','w')
i = 0
while i < len(x):
    new_file2.write(str(x[i]))
    new_file2.write(",")
    new_file2.write(str(y1[i]))
    new_file2.write(",")
    new_file2.write(str(roll1[i]))
    new_file2.write(",")
    new_file2.write(str(yaw7[i]))
    new_file2.write(",")
    new_file2.write(str(pitch1[i]))
    new_file2.write(str("\n"))
    i = i + 1
new_file2.close()


print 'changing pitch'
while p >= -80:
    xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, 0,p,0)
    print xyzrot[0]
    p = p - 10

p = 80
while p >= -80:
    xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, 0,p,0)
    print xyzrot[1]
    p = p - 10

print 'changing yaw'
while y >= -80:
    xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, 0,0,y)
    y = y - 10
    print xyzrot[0]

y = 80
while y >= -80:
    xyzrot = rotate3D(xtlnonrot,xuas, ytlnonrot, yuas, altitude, 0,0,y)
    y = y - 10
    print xyzrot[1]
