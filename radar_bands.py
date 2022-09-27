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

def diff2(x, dt):
    d2dt = np.zeros(len(x))
    for i in range(1,len(x)-1):
        d2dt[i] = (x[i+1] -2*x[i] + x[i-1] )/(dt**2)
    return d2dt

def diff24(x, dt):
    d2dt = np.zeros(len(x))
    for i in range(2,len(x)-2):
        d2dt[i] = (-x[i-2] + 16*x[i-1] -30*x[i] + 16*x[i+1] -x[i+2] )/(12*dt**2)
    return d2dt

txt_files = glob.glob('input/*.trn')
# print(txt_files)
dellfiles('output/*.csv')


for file_name in txt_files:
    enu_xyz = pd.read_csv(file_name,skiprows=[0,1], header=None).to_numpy()
    enu_azelr = np.transpose(pm.enu2aer(enu_xyz[:,0],enu_xyz[:,1],enu_xyz[:,2]))
    
    # Range 2pt
    range_dff2 = diff2(enu_azelr[:,2], sample_time)   
    range_band = np.sqrt(np.abs(range_dff2/range_error))

    # Range 4pt
    range_dff24 = diff24(enu_azelr[:,2], sample_time)   
    range_band4 = np.sqrt(np.abs(range_dff24/range_error))

    # Azimute 2pt
    az_dff2 = diff2(enu_azelr[:,0], sample_time)   
    az_band = np.sqrt((1000*np.pi/180)*np.abs(az_dff2/range_error))

    # Azimute 4pt
    az_dff24 = diff24(enu_azelr[:,0], sample_time)   
    az_band4 = np.sqrt((1000*np.pi/180)*np.abs(az_dff24/range_error))

    # Elev 2pt
    el_dff2 = diff2(enu_azelr[:,1], sample_time)   
    el_band = np.sqrt((1000*np.pi/180)*np.abs(el_dff2/range_error))

    # Elev 4pt
    el_dff24 = diff24(enu_azelr[:,1], sample_time)   
    el_band4 = np.sqrt((1000*np.pi/180)*np.abs(el_dff24/range_error))

    band = np.empty((len(el_band),3))
    band[:,0] = az_band
    band[:,1] = el_band
    band[:,2] = range_band

    df = pd.DataFrame(band)
    df.to_csv( 'out.csv', index=False, header=['az_band','el_band','r_band'],float_format="%.3f")

    print(band)
    break


time_array = np.linspace(0 , len(band),len(band)) 

# plt.plot(time_array, range_band, label="az_2pt")
# plt.plot(time_array, range_band4, label="az_4pt")

# plt.legend(loc="upper left")
# plt.show()

plt.plot(time_array, range_band, label="range_band_2pt")
plt.plot(time_array, range_band4, label="range_band_4pt")

plt.legend(loc="upper left")
plt.show()


# time_array = np.linspace(0 , len(band),len(band)) 
# print(len(band))
# plt.plot(time_array, band, label=["az","el","r"])

# plt.legend(loc="upper left")
# plt.show()