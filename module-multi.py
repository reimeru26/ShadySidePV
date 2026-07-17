"""
This program calculates the 'shadow' of four photovoltaik modules.
The module is located perpendicular to the surface (like a fence) and faces east and west.
Radiation intensity on the ground is calculated from PVGIS data (see file Timeseries_shadow_2023.csv).

Required files:
    - Timeseries_shadow_2023.csv 

Overall structure:
    - First part = variables declaration / file name for output picture / read in of PVGIS data 
                 => at the end: choose time frame of calculation
    - Function declaration
        - def make_shape(px, py): creates a poly surface based on 4 points (x-y coordinates)
                                  (This is for creating the shadow.)
        - def make_modules(a): creates a poly surface with offset in x-direction
                                (This is for plotting the PV modules in the final figure.)
        - def beleucht(mx, my, mz, myshade, mdiff, mdir): Run through the 2D lattice / calculate radiation intensity 
                                                            (In shadow region = assign only diffusive radiation)
        - def deklination(myday): Calculate the declination, i.e. the correction of the sun's angle for east/ west
                                due to shift of earth's axis of rotation
        - Main part: perform calculation / create 2D lattice for results / generate figure
    
Uwe Reimer, HS Emden-Leer / May 2025

This is version 02. New in this version:
    - added "deklination"
"""
################################################
### variables declaration
import pandas as pd
import math

import matplotlib.pyplot as plt
import matplotlib.cm as colorm # color map
from matplotlib.path import Path
import matplotlib.patches as patches

mypic_shadow = "shadow-4mod.png"    # file name for result picture

#### PV Module ###
mod_h1 = 0.55           # lower position / m
mod_h2 = 2.25 + mod_h1  # upper position (height) / m
mod_b  = 5.6            # width / m
offx = 10.0             # offset in x for placing the module
offy = 5.0              # offset in y for placing the module
distmod = 5.0            # distance between modules
#### internal
dx1 = 0.0   # shift in x -> height 1
dx2 = 0.0   # shift in x -> height 2
dy1 = 0.0   # shift in y -> height 1
dy2 = 0.0   # shift in y -> height 2
px = [0.0, 0.0, 0.0, 0.0]   # 4 corners x-pos
py = [0.0, 0.0, 0.0, 0.0]   # 4 corners y-pos
# check min and max values
mymin = 900000.0
mymax = 0.0

########################################################
### Set up of PVGIS data
# This is the time frame of the data set of the *.csv file
# Simulation time is chosen a few lines down.
sim_start = '2023-01-01 00:00'
sim_end = '2023-12-31 23:00'
year_start = sim_start
pv_gis = pd.read_csv('Timeseries_shadow_2023.csv', sep=',', skiprows = 8, nrows = 8769)
pv_gis.index = pd.date_range(start = sim_start, periods = len(pv_gis['T2m']), freq = 'h')

"""
### These are the rows from the *.csv file ###
Gb(i): Beam (direct) irradiance on the inclined plane (plane of the array) (W/m2)
Gd(i): Diffuse irradiance on the inclined plane (plane of the array) (W/m2)
Gr(i): Reflected irradiance on the inclined plane (plane of the array) (W/m2)
H_sun: Sun height (degree)
T2m: 2-m air temperature (degree Celsius)
WS10m: 10-m total wind speed (m/s)
Int: 1 means solar radiation values are reconstructed
"""
#print(pv_gis.info())

### Choose time frame of simulation
### Always calculate full days!

sim_start = '2023-04-05 00:00'
sim_end = '2023-04-05 23:00'

day = pv_gis[sim_start:sim_end]
day.reset_index(inplace=True, col_level=0, names="mydate") # change time index into a regular column 
#print(day.info())

def make_shape(px, py):
    ps = [
       ( px[0] , py[0] ),  # right, bottom
       ( px[2] , py[2] ),  # left, bottom
       ( px[3] , py[3] ),  # left, top
       ( px[1] , py[1] ),  # right, top       
       (0.0, 0.0)  # ignored
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY
    ]

    #myshade = Path(ps, codes)
    return Path(ps, codes)
#####################################################
def make_modules(a):
    """
    make a shape with offset a in x-coordiate
    for plotting the PV modules in the final figure
    """
    global offx, offy, mod_b, delta

    ps = [
       ( (offx + a)/ delta , offy/ delta ),  # left, bottom
       ( (offx + a)/ delta , (offy + mod_b) / delta ),  # left, top
       ( (offx + a + 0.2) / delta , (offy + mod_b)/ delta ),  # right, top
       ( (offx + a + 0.2) / delta , offy/ delta),  # right, bottom
       (0.0, 0.0)  # ignored
    ]

    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY
    ]

    return Path(ps, codes)
#####################################################

def beleucht(mx, my, mz, myshade1, myshade2, myshade3, myshade4, mdiff, mdir):
    # Belichte das Gitter -> wo ist Schatten, wo ist Licht
    j = 0
    for y in my:
        for x in mx:
            mys1 = myshade1.contains_points([(x,y)])
            mys2 = myshade2.contains_points([(x,y)])
            mys3 = myshade3.contains_points([(x,y)])
            mys4 = myshade4.contains_points([(x,y)])
            if mys1[0] or mys2[0] or mys3[0] or mys4[0]:
                c = mdiff
            else:
                c = mdir + mdiff
            
            mz[j] = mz[j] + c
            j = j + 1

#####################################################
def deklination(myday):
    # Abweichung der Position der Sonne (Ost-West) aufgrund der Ekliptik
    global year_start
    
    t = (myday - pd.Timestamp(year_start)).days
    #t = ( pd.Timestamp(myday) - pd.Timestamp(sim_start)).days
    a = ( 284 + t ) * 360 / 365
    a = math.radians(a)
    dekli = 23.45 * math.sin(a)
    
    return dekli

#####################################################
## make lattice

delta = 0.1
myxmax = 35.0
myymax = 20.0
mx = []
my = []
mz = []

a = 0.0
while a < (myxmax + delta):
    mx.append(a)
    a = a + delta
    
a = 0.0
while a < (myymax + delta):
    my.append(a)
    a = a + delta

for y in my:
    for x in mx:
        mz.append(0.0)

#############################
### Start main calculation 
#############################

i = 0
h = 0
while i < len(day):
    if day['Gd(i)'].iloc[i] > 0.0:                 # Wenn Streulicht da, dann steht Sonne am Himmel
        ah = math.radians( day['H_sun'].iloc[i] )  # Winkel Höhe Sonne
        dekli = deklination( day['mydate'].iloc[i] )
        if (h*15.0 - dekli) < 181.0:        # vormittag
            aow = math.radians( h*15.0 - dekli - 90.0 )  # Winkel ost-west, hier 0 Grad ist ost

            dx1 = (mod_h1) / math.tan(ah)
            dx2 = (mod_h2) / math.tan(ah)
            dy1 = dx1 * math.sin(aow)
            dy2 = dx2 * math.sin(aow)
            
            px[0] = offx - dx1 # unten
            px[1] = offx - dx1
            px[2] = offx - dx2 # oben
            px[3] = offx - dx2
            
            py[0] = offy + dy1
            py[1] = offy + dy1 + mod_b
            py[2] = offy + dy2
            py[3] = offy + dy2 + mod_b
            
        else:                   # nachmittag
            aow = math.radians( 360.0 - h*15.0 + dekli - 90.0 )  # Winkel West-Ost, also gespiegelt
            
            dx1 = (mod_h1) / math.tan(ah)
            dx2 = (mod_h2) / math.tan(ah)
            dy1 = dx1 * math.sin(aow)
            dy2 = dx2 * math.sin(aow)
            
            px[0] = offx + dx1 # unten
            px[1] = offx + dx1
            px[2] = offx + dx2 # oben
            px[3] = offx + dx2
            
            py[0] = offy + dy1
            py[1] = offy + dy1 + mod_b
            py[2] = offy + dy2
            py[3] = offy + dy2 + mod_b
                
        # Erzeuge 2D Schatten        
        myshade1 = make_shape(px, py)
        
        a = 0
        while a < 4:
            px[a] = px[a] + distmod
            a = a + 1
        myshade2 = make_shape(px, py)
        
        a = 0
        while a < 4:
            px[a] = px[a] + distmod
            a = a + 1
        myshade3 = make_shape(px, py)
        
        a = 0
        while a < 4:
            px[a] = px[a] + distmod
            a = a + 1
        myshade4 = make_shape(px, py)
        
        ### belichte das Gitter
        beleucht(mx, my, mz, myshade1, myshade2, myshade3, myshade4, day['Gd(i)'].iloc[i], float( day['Gb(i)'].iloc[i] ) )
        
    i = i + 1
    h = h + 1
    if h > 23:
        h = 0
        print(".", end="", flush=True)
        
# Create 2D array for results
mzz = []
i = 0
r = 0
for y in my:
    r = i
    for x in mx:
        i = i + 1
    mzz.append(mz[r:(i-1)])

# check min max values
for a in mz:
    if a > mymax: mymax = a
    if a < mymin: mymin = a
print(sim_start + " to " + sim_end)
print("Min = " + str(mymin) + "   Max = " + str(mymax) + "   Min/Max = " + str(mymin/mymax) )    

# Plot 2D
fig, ax = plt.subplots(figsize=(12, 6), layout='tight')
plt.pcolormesh(mzz, cmap='cubehelix')
plt.colorbar(label="Strahlung in W/m$^2$")

plt.ylim(0.0 , (myymax / delta) ) # set axis limit 
plt.xlim(0.0 , (myxmax / delta) ) 

myxtics = [50, 100, 150, 200, 250, 300]
myxtlab = ["5", "10", "15", "20", "25", "30"]
plt.xticks(ticks=myxtics, labels=myxtlab)
myytics = [0, 50, 100, 150, 200]
myytlab = ["0", "5", "10", "15", "20"]
plt.yticks(ticks=myytics, labels=myytlab)

mymod = make_modules(0 * distmod)
patch = patches.PathPatch(mymod, facecolor='orange')
ax.add_patch(patch)
mymod = make_modules(1 * distmod)
patch = patches.PathPatch(mymod, facecolor='orange')
ax.add_patch(patch)
mymod = make_modules(2 * distmod)
patch = patches.PathPatch(mymod, facecolor='orange')
ax.add_patch(patch)
mymod = make_modules(3 * distmod)
patch = patches.PathPatch(mymod, facecolor='orange')
ax.add_patch(patch)

plt.savefig(mypic_shadow)
