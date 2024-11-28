"""
Creator: Francisval Guedes Soares
Date: 2021
"""

import streamlit as st
from datetime import datetime
from lib.pgFunctions import*

def main():
    """main function that provides the simplified interface for configuration,
         visualization and data download. """  

    st.set_page_config(
    page_title="Conversão de coordenadas",
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

    st.title("Calculo de banda")
    st.subheader('**Conversão de coordenadas**')

    st.markdown('suport: Francisval Guedes Soares, Email: francisvalg@gmail.com')
    
    # url = "https://github.com/francisvalguedes/coordConverter.git"
    # st.markdown("Repositório: [github.com/francisvalguedes/coordConverter](%s)" % url)

    ## Descrição                
    st.markdown("""
    Aplicação web desenvolvida com Streamlit que permite.       
    """)

    st.markdown('Novos pontos de referências podem ser cadastrados na barra lateral')
    st.markdown('Pontos de referência no WGS84 já cadastrados:')
    st.session_state.lc_df = pd.read_csv('data/confLocalWGS84.csv').dropna(how='all')
    st.dataframe(st.session_state.lc_df.style.format({'lat': '{:.6f}', 'lon': '{:.6f}', 'height': '{:.2f}'}))

    #Cadastra sensor sidebar
    sensor_registration()

        
if __name__== '__main__':
    main()



