"""
Creator: Francisval Guedes Soares
Date: 2021
"""

import streamlit as st
from datetime import datetime
from lib.pgFunctions import*

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

def main():
    """main function that provides the simplified interface for configuration,
         visualization and data download. """  

    st.set_page_config(
    page_title="Análise de Trajetórias",
    page_icon="🌏", # "🤖",  # "🧊",
    # https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.sitelink.com',
    #     'Report a bug': "https://www.sitelink.com",
    #     'About': "# A cool app"
    # }
    )     

    st.title("Análise de dados de trajetórias nominais")
    # st.subheader('**Conversão de coordenadas**')

    st.markdown('suporte: Francisval Guedes Soares, Email: francisvalg@gmail.com')
    
    # url = "https://github.com/francisvalguedes/coordConverter.git"
    # st.markdown("Repositório: [github.com/francisvalguedes/coordConverter](%s)" % url)

    ## Descrição                
    st.markdown("""
    Aplicação web desenvolvida com Streamlit que permite análisar dados de trajetórias nominais sem ruído.     
    """)

    st.markdown('Novos pontos de referências podem ser cadastrados na barra lateral')
    st.markdown('Pontos de referência no WGS84 já cadastrados:')
    st.session_state.lc_df = pd.read_csv('data/confLocalWGS84.csv').dropna(how='all')
    st.dataframe(st.session_state.lc_df.style.format({'lat': '{:.6f}', 'lon': '{:.6f}', 'height': '{:.2f}'}))

    #Cadastra sensor sidebar
    sensor_registration()

        
if __name__== '__main__':
    main()



