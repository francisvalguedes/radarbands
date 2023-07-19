import glob
import pandas as pd
import re
from datetime import datetime, timedelta
import numpy as np
import os
import pymap3d as pm
import matplotlib.pyplot as plt

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

def gms_to_decimal(s):
    angle_gms = re.split('[°\' "]+', s)
    dd = 0
    for i in range(3):
        dd+= np.sign(float(angle_gms[0]))*abs(float(angle_gms[i])/(60**i))
    return dd

sample_time = 1
range_error_m = 25
erro_angular_mrd = 10

# Ellipsoid
wgs72 = pm.Ellipsoid(model='wgs72')

# Trajetory origin point
# Rampa: Lançador wgs72
orig_point = {"lat": "-5°55'18.8359", "lon": "-35°9'41.395", "heigh": 45}
#orig_point = {"lat": "-2°18'57.89", "lon": "-44°22'5.99", "heigh": 42}

orig_point["lat"] = gms_to_decimal(orig_point["lat"])
orig_point["lon"] = gms_to_decimal(orig_point["lon"])

# Sensor: Radar wgs72
radar_point = {"lat": "-5°55'10.3734", "lon": "-35°10'25.2836", "heigh": 59.13}

radar_point["lat"] = gms_to_decimal(radar_point["lat"])
radar_point["lon"] = gms_to_decimal(radar_point["lon"])

print(orig_point)
print(radar_point)


txt_files = glob.glob('input/*.trn')
print(txt_files)
dellfiles('output/*.csv')
dellfiles('output/*.png')

for file_name in txt_files:
    enu_xyz_orig = pd.read_csv(file_name,skiprows=[0], header=None).to_numpy()

    ecef = np.transpose(pm.enu2ecef(enu_xyz_orig[:,0],
                                    enu_xyz_orig[:,1],
                                    enu_xyz_orig[:,2],
                                    orig_point["lat"],
                                    orig_point["lon"],
                                    orig_point["heigh"],
                                    wgs72))
    enu_xyz_radar = np.transpose( pm.ecef2enu(
                                ecef[:,0],
                                ecef[:,1],
                                ecef[:,2],
                                radar_point["lat"],
                                radar_point["lon"],
                                radar_point["heigh"],
                                wgs72))

    enu_azelr_radar = np.transpose(pm.enu2aer(enu_xyz_radar[:,0],
                                        enu_xyz_radar[:,1],
                                        enu_xyz_radar[:,2],
                                        deg=True
                                        ))

    enu_azelr = enu_azelr_radar
    # velocity    
    # Azimute
    az_dff = np.diff(enu_azelr[:,0], n=1) / sample_time
    # Elev
    el_dff = np.diff(enu_azelr[:,1], n=1) / sample_time
    # Range
    range_dff = np.diff(enu_azelr[:,2], n=1) / sample_time 

    # acceleration
    # Azimute
    az_dff2 = np.diff(enu_azelr[:,0], n=2) / sample_time
    # Elev
    el_dff2 = np.diff(enu_azelr[:,1], n=2) / sample_time
    # Range
    range_dff2 = np.diff(enu_azelr[:,2], n=2) / sample_time 

    band = np.zeros((len(az_dff2),3))
    band[:,0] = np.sqrt((1000*np.pi/180)*np.abs(az_dff2/erro_angular_mrd))
    band[:,1] = np.sqrt((1000*np.pi/180)*np.abs(el_dff2/erro_angular_mrd))
    band[:,2] = np.sqrt(np.abs(range_dff2/range_error_m))

    band_aq = np.zeros((len(az_dff),3))
    band_aq[:,0] = np.sqrt((1000*np.pi/180)*np.abs(az_dff/erro_angular_mrd)) # az
    band_aq[:,1] = np.sqrt((1000*np.pi/180)*np.abs(el_dff/erro_angular_mrd)) # el
    band_aq[:,2] = np.sqrt(np.abs(range_dff/range_error_m)) # range

    # save data

    df_band = pd.DataFrame(band)
    df_band.to_csv( 'out.csv', index=False, header=['az_band','el_band','r_band'],float_format="%.3f")

    df_band_aq = pd.DataFrame(band)
    df_band_aq.to_csv( 'out.csv', index=False, header=['az_band_aq','el_band_aq','r_band_aq'],float_format="%.3f")

    # print(band)
    time_array = np.linspace(1 , len(az_dff),len(az_dff)) 

    figure, axis = plt.subplots(3, 3)
    figure.suptitle('Profile and bands, Trajectory: ' + file_name.split(os.path.sep)[-1])

    axis[0, 0].plot(time_array, el_dff, label="El_sp")
    axis[0, 0].set_title("Elevation speed(m/s)")
    axis[0, 1].plot(time_array, az_dff, label="Az_sp")
    axis[0, 1].set_title("Azimuth speed(m/s)")
    axis[0, 2].plot(time_array, range_dff, label="Range_sp")
    axis[0, 2].set_title("Range speed(m/s)")

    time_array = np.linspace(2 , len(band_aq),len(band_aq)) 

    axis[1, 0].plot(time_array, band_aq[:,1], label="El")
    axis[1, 0].set_title("Elevation aq. band(mrad/s^2)")
    axis[1, 1].plot(time_array, band_aq[:,0], label="Az")
    axis[1, 1].set_title("Azimuth aq. band(mrad/s^2)")
    axis[1, 2].plot(time_array, band_aq[:,2], label="Range")
    axis[1, 2].set_title("Range aq. band(m/s^2)")

    time_array = np.linspace(2 , len(band),len(band)) 

    axis[2, 0].plot(time_array, band[:,1], label="El")
    axis[2, 0].set_title("Elevation band(mrad/s^2)")
    axis[2, 1].plot(time_array, band[:,0], label="Az")
    axis[2, 1].set_title("Azimuth band(mrad/s^2)")
    axis[2, 2].plot(time_array, band[:,2], label="Range")
    axis[2, 2].set_title("Range band(m/s^2)")


    figure.set_size_inches(18, 8)


    plt.subplots_adjust(#left=0.1, 
                        #bottom=0.1,  
                        #right=0.9,  
                        #top=0.9,  
                        wspace=0.25,  
                        hspace=0.45) 

    # plt.subplot_tool() 
    #plt.legend(loc="upper left")
    plt.savefig('output' + os.path.sep + file_name.split(os.path.sep)[-1] + '.png')    
    # plt.show()