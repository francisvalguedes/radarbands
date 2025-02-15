import streamlit as st
import pandas as pd
import re
from lib.constants import  ConstantsNamespace

cn = ConstantsNamespace()

@st.cache_data
def pd_csv_read(caminho_csv):
    return pd.read_csv(caminho_csv).dropna(how='all')

def sensor_registration():
    # adicionar novo ponto de referência (sensor)
    lc_expander = st.sidebar.expander("Adicionar novo ponto de referência no WGS84", expanded=False)
    lc_name = lc_expander.text_input('Nome', "minha localização")
    latitude = lc_expander.number_input('Latitude', -90.0, 90.0, 0.0, format="%.6f")
    longitude = lc_expander.number_input('Longitude', -180.0, 180.0, 0.0, format="%.6f")
    height = lc_expander.number_input('Altura (m)', -1000.0, 2000.0, 0.0, format="%.6f")
    #color = lc_expander.text_input('Cor', "red")
    if lc_expander.button("Registrar nova localização"):
        lc_add = {'name': [lc_name], 'lat': [latitude], 'lon': [longitude], 'height': [height]} # , 'color': [color]
        if lc_name not in st.session_state.lc_df['name'].to_list():
            if re.match('^[A-Za-z0-9_-]*$', lc_add['name'][0]):
                st.session_state.lc_df = pd.concat([st.session_state.lc_df, pd.DataFrame(lc_add)], axis=0)
                st.session_state.lc_df.to_csv('data/confLocalWGS84.csv', index=False)
                lc_expander.write('Localização registrada')
            else:
                lc_expander.write('Escreva um nome sem caracteres especiais')
        else:
            lc_expander.write('Localização já existe')

