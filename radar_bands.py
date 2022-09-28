import glob
import pandas as pd
# import re
from datetime import datetime, timedelta
import numpy as np
import os
import pymap3d as pm
import matplotlib.pyplot as plt

sample_time = 1
range_error = 25

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

txt_files = glob.glob('input/*.trn')
# print(txt_files)
dellfiles('output' + os.path.sep +'*.png')

for file_name in txt_files:
    enu_xyz = pd.read_csv(file_name,skiprows=[0,1], header=None).to_numpy()
    enu_azelr = np.transpose(pm.enu2aer(enu_xyz[:,0],enu_xyz[:,1],enu_xyz[:,2]))
    
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
    az_band = np.sqrt((1000*np.pi/180)*np.abs(az_dff2/range_error))

    # Elev
    el_dff2 = np.diff(enu_azelr[:,1], n=2) / sample_time  
    el_band = np.sqrt((1000*np.pi/180)*np.abs(el_dff2/range_error))

    # Range
    range_dff2 = np.diff(enu_azelr[:,2], n=2) / sample_time 
    range_band = np.sqrt(np.abs(range_dff2/range_error))


    band = np.empty((len(el_band),3))
    band[:,0] = az_band
    band[:,1] = el_band
    band[:,2] = range_band

    # df = pd.DataFrame(band)
    # df.to_csv( 'out.csv', index=False, header=['az_band','el_band','r_band'],float_format="%.3f")

    # print(band)
    time_array = np.linspace(0 , len(az_dff),len(az_dff)) 

    figure, axis = plt.subplots(2, 3)
    figure.suptitle('Profile and bands, NORAD:' + file_name.split(os.path.sep)[-1])
    axis[0, 0].plot(time_array, az_dff, label="Az_sp")
    axis[0, 0].set_title("Azimuth speed(m/s)")
    axis[0, 1].plot(time_array, el_dff, label="El_sp")
    axis[0, 1].set_title("Elevation speed(m/s)")
    axis[0, 2].plot(time_array, range_dff, label="Range_sp")
    axis[0, 2].set_title("Range speed(m/s)")

    time_array = np.linspace(0 , len(az_band),len(az_band)) 

    axis[1, 0].plot(time_array, az_band, label="Az")
    axis[1, 0].set_title("Azimuth band(mrad/s^2)")
    axis[1, 1].plot(time_array, el_band, label="El")
    axis[1, 1].set_title("Elevation band(mrad/s^2)")
    axis[1, 2].plot(time_array, range_band, label="Range")
    axis[1, 2].set_title("Range band(m/s^2)")

    figure.set_size_inches(18, 5)


    plt.subplots_adjust(#left=0.1, 
                        #bottom=0.1,  
                        #right=0.9,  
                        #top=0.9,  
                        wspace=0.25,  
                        hspace=0.45) 

    # plt.subplot_tool() 
    #plt.legend(loc="upper left")
    plt.savefig('output' + os.path.sep + file_name.split(os.path.sep)[-1] + '.png')    
    #plt.show()