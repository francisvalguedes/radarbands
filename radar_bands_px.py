import glob
import pandas as pd
import re
from datetime import datetime, timedelta
import numpy as np
import os
import pymap3d as pm
import matplotlib.pyplot as plt
import sys

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
    """
    Converte angulos em graus, minutos e segundos para float
    Parameters
    ----------
    s - string ex: -5°55'00.000
    Returns
    -------
    angulo : float
    """
    angle_gms = re.split('[°\' "]+', s)
    dd = 0
    for i in range(3):
        dd+= np.sign(float(angle_gms[0]))*abs(float(angle_gms[i])/(60**i))
    return dd

def fit_coord(coord_ref):
    """
    Função ajustar e converter arquivo de configuração dos pontos de referência
    """
    for index, row in coord_ref.iterrows():
        if not isinstance(coord_ref.loc[index]['lat'], float):
            try:
                coord_ref.at[index,'lat'] = gms_to_decimal(coord_ref.loc[index]['lat'])
            except:
                print("error: coord_ref.csv file is not in proper angle format")
                sys. exit()
            try:
                coord_ref.at[index,'lon'] = gms_to_decimal(coord_ref.loc[index]['lon'])
            except:
                print("error: coord_ref.csv file is not in proper angle format")
                sys. exit()
        if coord_ref.loc[index]['ellipsoid'] not in ['wgs72','wgs84']:
            print("error: coord_ref.csv ellipsoid: wgs72' or 'wgs84")
            sys. exit()
        if  not isinstance(coord_ref.loc[index]['height'], float):
            print("error: coord_ref.csv height must be float")
            sys. exit()
    return coord_ref


# Configurações
# ******************************************
sample_time = 1
range_error_m = 25
erro_angular_mrd = 10

sensor_sel = 'Bearn-CLBI' # Sensor
ramp_sel = 'Bearn-CLBI' # 'Bearn-CLBI' 'LMU-CLBI-2' # Rampa

c_ref = pd.read_csv( 'conf/coord_ref.csv')

# Fim das configurações
# ******************************************

# Execução do script
print('\n')
print('arquivo coord_ref:')
print(c_ref)
c_ref = fit_coord(c_ref)
print('\n')
print('coordenadas em decimal:')
print(c_ref)
print('\n')

c_ref.to_csv('conf/coord_ref_d.csv', index= False)

if len(c_ref[c_ref['name'].str.contains(ramp_sel)].index):
    if len(c_ref[c_ref['name'].str.contains(sensor_sel)].index):
        # c_ref = c_ref[c_ref['name'].str.contains(ramp_sel) + c_ref['name'].str.contains(sensor_sel)] 
        c_ref = pd.concat([c_ref[c_ref['name'].str.contains(ramp_sel)],
                           c_ref[c_ref['name'].str.contains(sensor_sel)]])
        c_ref.set_index([pd.Index(['RAMP', 'SENS'])], inplace=True)
    else:
        print('não existe no arquivo o sensor ' + sensor_sel )
        sys.exit()
else:
    print('não existe no arquivo a rampa ' + ramp_sel )
    sys.exit()

coord_ref = c_ref
print('\n')
print('coord_ref FILE:')
print(coord_ref)
txt_files = glob.glob('input/*.trn')

dellfiles('output/*.csv')
dellfiles('output/*.png')
dellfiles('output/*.trn')


resume = {"NAME":[], "SITE_AQ":[],"GISE_AQ":[], "DIST_AQ":[],"SITE":[],"GISE":[],
                    "DIST":[]}

for file_name in txt_files:
    enu_xyz_orig = pd.read_csv(file_name,skiprows=[0], header=None).to_numpy()

    ecef = np.transpose(pm.enu2ecef(enu_xyz_orig[:,0],
                                    enu_xyz_orig[:,1],
                                    enu_xyz_orig[:,2],
                                    coord_ref.loc['RAMP']["lat"],
                                    coord_ref.loc['RAMP']["lon"],
                                    coord_ref.loc['RAMP']["height"],
                                    pm.Ellipsoid.from_name(coord_ref.loc['RAMP']["ellipsoid"])
                                    # pm.Ellipsoid(model=coord_ref.loc['RAMP']["ellipsoid"])
                                    ))
    enu_xyz_radar = np.transpose( pm.ecef2enu(
                                ecef[:,0],
                                ecef[:,1],
                                ecef[:,2],
                                coord_ref.loc['SENS']["lat"],
                                coord_ref.loc['SENS']["lon"],
                                coord_ref.loc['SENS']["height"],
                                pm.Ellipsoid.from_name(coord_ref.loc['SENS']["ellipsoid"])
                                #pm.Ellipsoid(model=coord_ref.loc['SENS']["ellipsoid"])
                                ))
    
    enu_xyz_radar_df = pd.DataFrame(enu_xyz_radar, columns=['X', 'Y', 'Z'] )
    enu_xyz_radar_df.to_csv( 'output' + os.path.sep + file_name.split(os.path.sep)[-1] + '_sensor_xyz.trn', index=False, float_format="%.3f" )
     

    enu_azelr_radar = np.transpose(pm.enu2aer(enu_xyz_radar[:,0],
                                        enu_xyz_radar[:,1],
                                        enu_xyz_radar[:,2],
                                        deg=True
                                        ))
    
    enu_azelr_radar_df = pd.DataFrame(enu_azelr_radar, columns=['GISE', 'SITE', 'DIST'] )
    enu_azelr_radar_df = enu_azelr_radar_df[['SITE', 'GISE', 'DIST']]
    enu_azelr_radar_df.to_csv( 'output' + os.path.sep + file_name.split(os.path.sep)[-1] + '_sensor_sgd.csv', index=False )


    # velocity    
    # Azimute
    az_dff = np.diff(enu_azelr_radar[:,0], n=1) / sample_time
    # Elev
    el_dff = np.diff(enu_azelr_radar[:,1], n=1) / sample_time
    # Range
    range_dff = np.diff(enu_azelr_radar[:,2], n=1) / sample_time 

    # acceleration
    # Azimute
    az_dff2 = np.diff(enu_azelr_radar[:,0], n=2) / sample_time
    # Elev
    el_dff2 = np.diff(enu_azelr_radar[:,1], n=2) / sample_time
    # Range
    range_dff2 = np.diff(enu_azelr_radar[:,2], n=2) / sample_time 

    band = np.zeros((len(az_dff2),3))
    band[:,0] = np.sqrt((1000*np.pi/180)*np.abs(az_dff2/erro_angular_mrd))
    band[:,1] = np.sqrt((1000*np.pi/180)*np.abs(el_dff2/erro_angular_mrd))
    band[:,2] = np.sqrt(np.abs(range_dff2/range_error_m))

    band_aq = np.zeros((len(az_dff),3))
    band_aq[:,0] = np.sqrt((1000*np.pi/180)*np.abs(az_dff/erro_angular_mrd)) # az
    band_aq[:,1] = np.sqrt((1000*np.pi/180)*np.abs(el_dff/erro_angular_mrd)) # el
    band_aq[:,2] = np.sqrt(np.abs(range_dff/range_error_m)) # range

    resume["NAME"].append(file_name.split(os.path.sep)[-1])
    resume["SITE_AQ"].append(np.max(band_aq[:,1]))
    resume["GISE_AQ"].append(np.max(band_aq[:,0]))
    resume["DIST_AQ"].append(np.max(band_aq[:,2]))
    resume["SITE"].append(np.max(band[:,1]))
    resume["GISE"].append(np.max(band[:,0]))
    resume["DIST"].append(np.max(band[:,2]))

# save data

    # df_band = pd.DataFrame(band)
    # df_band.to_csv('output' + os.path.sep + file_name.split(os.path.sep)[-1] + 'band.csv',
    #                index=False, header=['az_band','el_band','r_band'],float_format="%.3f")

    # df_band_aq = pd.DataFrame(band)
    # df_band_aq.to_csv( 'output' + os.path.sep + file_name.split(os.path.sep)[-1] + 'band_aq.csv',
    #                   index=False, header=['az_band_aq','el_band_aq','r_band_aq'],float_format="%.3f")

# plot bands
    time_array = np.linspace(1 , len(az_dff),len(az_dff)) 

    figure, axis = plt.subplots(3, 3)
    figure.suptitle('Profile and bands, Trajectory: ' + file_name.split(os.path.sep)[-1])

    axis[0, 0].plot(time_array, el_dff, label="El_sp")
    axis[0, 0].set_title("Site speed(deg/s)")
    axis[0, 1].plot(time_array, az_dff, label="Az_sp")
    axis[0, 1].set_title("Gise speed(deg/s)")
    axis[0, 2].plot(time_array, range_dff, label="Range_sp")
    axis[0, 2].set_title("Dist speed(m/s)")

    time_array = np.linspace(2 , len(band_aq),len(band_aq)) 

    axis[1, 0].plot(time_array, band_aq[:,1], label="El")
    axis[1, 0].set_title("Site aq. band(mrad/s^2)")
    axis[1, 1].plot(time_array, band_aq[:,0], label="Az")
    axis[1, 1].set_title("Gise aq. band(mrad/s^2)")
    axis[1, 2].plot(time_array, band_aq[:,2], label="Range")
    axis[1, 2].set_title("Dist aq. band(m/s^2)")

    time_array = np.linspace(2 , len(band),len(band)) 

    axis[2, 0].plot(time_array, band[:,1], label="El")
    axis[2, 0].set_title("Site band(mrad/s^2)")
    axis[2, 1].plot(time_array, band[:,0], label="Az")
    axis[2, 1].set_title("Gise band(mrad/s^2)")
    axis[2, 2].plot(time_array, band[:,2], label="Range")
    axis[2, 2].set_title("Dist band(m/s^2)")


    figure.set_size_inches(18, 8)


    plt.subplots_adjust(#left=0.1, 
                        #bottom=0.1,  
                        #right=0.9,  
                        #top=0.9,  
                        wspace=0.25,  
                        hspace=0.45) 

    # plt.subplot_tool() 
    # plt.legend(loc="upper left")
    plt.savefig('output' + os.path.sep + file_name.split(os.path.sep)[-1] + '.png')    

df_resume = pd.DataFrame(resume)
pd.set_option('display.precision', 2)
print('\n')
print('MAXIMUM BANDS:')
print(df_resume)
print('\n')
df_resume.to_csv( 'output' + os.path.sep + 'resume_bands.csv',
                    index=False, float_format="%.3f")

coord_ref.to_csv( 'output' + os.path.sep + 'coord_ref_o.csv',
                    index=True)
    
print('Calculations performed successfully, results in the output folder!')
