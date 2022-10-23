import glob
import pandas as pd
# import re
from datetime import datetime, timedelta
import numpy as np
import os
import pymap3d as pm
import matplotlib.pyplot as plt
import re

def gms_to_decimal(s):
    angle_gms = re.split('[°\' "]+', s)
    dd = 0
    for i in range(3):
        dd+= np.sign(float(angle_gms[0]))*abs(float(angle_gms[i])/(60**i))
    return dd


sample_time = 1
range_error = 25

# Trajetory origin point
wgs72 = pm.Ellipsoid(model='wgs72')
orig_point = {"lat": "-2°18'57.89", "lon": "-44°22'5.99", "heigh": 42}
orig_point["lat"] = gms_to_decimal(orig_point["lat"])
orig_point["lon"] = gms_to_decimal(orig_point["lon"])

# Radar point -5.919483, -35.173647
wgs84 = pm.Ellipsoid(model='wgs84')
radar_point = {"lat": -5.919483, "lon": -35.173647, "heigh": 59}

print(orig_point)
print(radar_point)

def dellfiles(file):
    py_files = glob.glob(file)
    err = 0
    for py_file in py_files:
        try:
            os.remove(py_file)
        except OSError as e:
            print(f"Error:{e.strerror}")
            err = e.strerror
    return err

txt_files = glob.glob('coord_conv/*.trn')
# print(txt_files)
dellfiles('input' + os.path.sep +'*.trn')

for file_name in txt_files:
    enu_xyz = pd.read_csv(file_name,skiprows=[0,1], header=None).to_numpy()
    ecef = np.transpose(pm.enu2ecef(enu_xyz[:,0],
                                    enu_xyz[:,1],
                                    enu_xyz[:,2],
                                    orig_point["lat"],
                                    orig_point["lon"],
                                    orig_point["heigh"],
                                    wgs72))
    enu_xyz_wgs84_radar = np.transpose( pm.ecef2enu(ecef[:,0],
                                ecef[:,1],
                                ecef[:,2],
                                radar_point["lat"],
                                radar_point["lon"],
                                radar_point["heigh"],
                                wgs84))

    enu_azelr = np.transpose(pm.enu2aer(enu_xyz_wgs84_radar[:,0],
                                        enu_xyz_wgs84_radar[:,1],
                                        enu_xyz_wgs84_radar[:,2]
                                        ))
    df = pd.DataFrame( enu_azelr)                           
    df.to_csv( 'input'+ os.path.sep + file_name.split(os.path.sep)[-1], index=False, header=[str(len(df.index)-1),'1000','1'],float_format="%.3f")
    # df.to_csv( 'input'+ os.path.sep + file_name.split(os.path.sep)[-1], index=False, header=[str(len(df.index)-1),'1000','1'],float_format="%.3f")