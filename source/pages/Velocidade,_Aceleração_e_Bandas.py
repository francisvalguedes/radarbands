"""
Creator: Francisval Guedes Soares
Date: 2024
"""

import streamlit as st
import pandas as pd
import re
import numpy as np
import pymap3d as pm

from lib.constants import  ConstantsNamespace
from lib.pgFunctions import*

import plotly.graph_objects as go
from plotly.subplots import make_subplots

cn = ConstantsNamespace()

def enu1_to_enu2(enu_rampa, ref_rampa, ref_sensor):
    ell=pm.Ellipsoid.from_name('wgs84')
    ecef = np.transpose(pm.enu2ecef(enu_rampa[:,0],
                                    enu_rampa[:,1],
                                    enu_rampa[:,2],
                                    ref_rampa["lat"],
                                    ref_rampa["lon"],
                                    ref_rampa["height"],
                                    ell=ell
                                    ))
    enu_sensor = np.transpose( pm.ecef2enu(
                                ecef[:,0],
                                ecef[:,1],
                                ecef[:,2],
                                ref_sensor["lat"],
                                ref_sensor["lon"],
                                ref_sensor["height"],
                                ell=ell
                                ))
    enu_azelr_radar = np.transpose(pm.enu2aer(enu_sensor[:,0],
                                        enu_sensor[:,1],
                                        enu_sensor[:,2],
                                        deg=False
                                        ))    
    enu_sensor = np.hstack((enu_sensor, enu_azelr_radar))
    return pd.DataFrame(enu_sensor, columns=['x', 'y', 'z', 'Az', 'El', 'd'])


def calculate_velocity_acceleration(df, sampling_time, erro_angular_mrd, erro_d_m ):
    """
    Calcula a velocidade e aceleração para cada eixo e para as variáveis angulares (Az, El, r),
    e adiciona o tempo relativo ao primeiro ponto.

    Args:
        df (pd.DataFrame): DataFrame contendo as colunas 'x', 'y', 'z', 'Az', 'El', 'd'.
        sampling_time (float): Intervalo de tempo entre amostras (em segundos).

    Returns:
        pd.DataFrame: DataFrame com as colunas:
                      ['X(m)', 'Y(m)', 'Z(m)', 'VX(m/s)', 'VY(m/s)', 'VZ(m/s)', 
                       'AX(m/s²)', 'AY(m/s²)', 'AZ(m/s²)', 'Az', 'El', 'd', 
                       'Vaz(rad/s)', 'Vel(rad/s)', 'Vr(m/s)', 
                       'Aaz(rad/s²)', 'Ael(rad/s²)', 'Ar(m/s²)', 'Tempo (s)'].
    """
    # Calcular as diferenças das posições divididas pelo tempo de amostragem (velocidade)
    velocity_x = np.gradient(df['x'], sampling_time)
    velocity_y = np.gradient(df['y'], sampling_time)
    velocity_z = np.gradient(df['z'], sampling_time)

    # Ajustar descontinuidade angular para Az usando np.unwrap
    az_unwrapped = np.unwrap(df['Az'])  # Remove descontinuidade de 2pi em Az
    
    # Calcular as diferenças das variáveis angulares (Az, El, r) divididas pelo tempo (velocidade angular)
    velocity_az = np.gradient(az_unwrapped, sampling_time)  # Velocidade angular Azimute
    velocity_el = np.gradient(df['El'], sampling_time)  # Velocidade angular Elevação
    velocity_r = np.gradient(df['d'], sampling_time)    # Velocidade radial
   
    # Calcular as diferenças das velocidades divididas pelo tempo de amostragem (aceleração)
    acceleration_x = np.gradient(velocity_x, sampling_time)
    acceleration_y = np.gradient(velocity_y, sampling_time)
    acceleration_z = np.gradient(velocity_z, sampling_time)
    
    # Calcular as acelerações angulares (derivadas das velocidades angulares)
    acceleration_az = np.gradient(velocity_az, sampling_time)  # Aceleração angular Azimute
    acceleration_el = np.gradient(velocity_el, sampling_time)  # Aceleração angular Elevação
    acceleration_r = np.gradient(velocity_r, sampling_time)    # Aceleração radial

    band_az = np.sqrt(1000*np.abs(acceleration_az/erro_angular_mrd))
    band_el = np.sqrt(1000*np.abs(acceleration_el/erro_angular_mrd))
    band_d = np.sqrt(np.abs(acceleration_r/erro_d_m))

    band_aq_az = np.sqrt(1000*np.abs(velocity_az/erro_angular_mrd)) # az
    band_aq_el = np.sqrt(1000*np.abs(velocity_el/erro_angular_mrd)) # el
    band_aq_d = np.sqrt(np.abs(velocity_r/erro_d_m)) # range

    # Criar um vetor de tempo relativo ao primeiro ponto
    time_relative = np.arange(0, len(df) * sampling_time, sampling_time)
    
    # Garantir que o vetor de tempo tenha o mesmo comprimento do DataFrame
    time_relative = time_relative[:len(df)]
    
    # Criar um novo DataFrame com os resultados
    result_df = pd.DataFrame({
        'TR(s)': time_relative,
        'X(m)': df['x'],
        'Y(m)': df['y'],
        'Z(m)': df['z'],
        'VX(m/s)': velocity_x,
        'VY(m/s)': velocity_y,
        'VZ(m/s)': velocity_z,
        'AX(m/s²)': acceleration_x,
        'AY(m/s²)': acceleration_y,
        'AZ(m/s²)': acceleration_z,
        'Az(rad)': az_unwrapped, #df['Az'],
        'El(rad)': df['El'],
        'd(m)': df['d'],
        'Vaz(rad/s)': velocity_az,
        'Vel(rad/s)': velocity_el,
        'Vr(m/s)': velocity_r,
        'Aaz(rad/s²)': acceleration_az,
        'Ael(rad/s²)': acceleration_el,
        'Ar(m/s²)': acceleration_r,
        'BandaAq_Az(mrad/s²)': band_aq_az,
        'BandaAq_El(mrad/s²)': band_aq_el,
        'BandaAq_d(m/s²)': band_aq_d,
        'Banda_Az(mrad/s²)': band_az,
        'Banda_El(mrad/s²)': band_el,
        'Banda_d(m/s²)': band_d     
    })   

    return result_df


def plot_streamlit_plotly(df, plot_seq, titulo = 'Gráficos Interativos'):
    """
    Gera 9 gráficos interativos (usando Plotly) para cada coluna do DataFrame fornecido, exceto a coluna de tempo ('Tempo (s)'),
    e exibe os gráficos na interface do Streamlit com interatividade (zoom, pan, hover).

    Args:
        df (pd.DataFrame): DataFrame com as colunas a serem plotadas. Deve conter uma coluna 'Tempo (s)'.
    """
    # # Determinar a sequência de colunas a serem plotadas (excluindo 'Tempo (s)')
    # plot_seq = df.columns.difference(['TR(s)'])
    
    # Criar uma figura com 9 subplots (usando o Layout do Plotly)
    fig = make_subplots(rows=3, cols=3, subplot_titles=plot_seq)
    
    # Adicionar gráficos para cada coluna do DataFrame
    for i, col_name in enumerate(plot_seq):
        row = i // 3 + 1  # Linha (1 a 3)
        col = i % 3 + 1   # Coluna (1 a 3)
        
        # Adicionar linha de dados para o gráfico interativo
        fig.add_trace(
            go.Scatter(x=df['TR(s)'], y=df[col_name], mode='lines', name=col_name),
            row=row, col=col
        )
    
    # Atualizar layout para melhorar a visualização
    fig.update_layout(
        height=900, width=1200,  # Tamanho total da figura
        title_text=titulo,
        showlegend=False,
        title_x=0.5,
        template="plotly" # "plotly_dark"  # Tema de fundo escuro (opcional)
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)




def main(): 
# configuração da página   
    st.set_page_config(
    page_title="Velocidade, Aceleração e Bandas",
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

# cabeçalho
    st.title("Cálculo de Velocidade, Aceleração e Bandas")
    st.subheader('**Entrada de Configurações**')
    
    # st.markdown('Cálculo de Bandas passante para controle de servo')

    st.session_state.lc_df = pd.read_csv('data/confLocalWGS84.csv')

    #Cadastra sensor sidebar
    sensor_registration()

# verifica se foi escolhido o sensor
    #st.session_state.sensores = st.multiselect('Escolha os sensores para conversão', st.session_state.lc_df['name'].tolist())
    st.session_state.rampa = st.selectbox("Escolha o ponto de referência de origem - Rampa (ENU¹)",st.session_state.lc_df['name'].tolist(),)
    st.session_state.sensor = st.selectbox("Escolha o ponto de referência de destino - Sensor (ENU²)",st.session_state.lc_df['name'].tolist(), index=1)    
   
    # Entrada numérica para erro angular em miliradianos
    erro_angular = st.number_input('Erro Angular (miliradianos)', min_value=0.0, max_value=100.0, value=10.0, step=0.1)

    # Entrada numérica para erro de distância em metros
    erro_distancia = st.number_input('Erro de Distância (metros)', min_value=0.0, max_value=1000.0, value=25.0, step=0.1)

    # Entrada numérica para erro de distância em metros
    tempo_amostra = st.number_input('Tempo de amostragem (s)', min_value=0.01, max_value=10.0, value=1.0, step=0.01)

    # Exibir os valores inseridos
    # st.write(f"Erro Angular: {erro_angular} miliradianos")
    # st.write(f"Erro de Distância: {erro_distancia} metros")


# carregar arquivo de pontos a serem convertidos
    st.markdown("""
    #### Arquivo a ser carregado:
    1. O arquivo de texto deve conter as colunas 'x', 'y', 'z' no referencial da rampa, a primeira linha é iguinorada.
    2. O tempo de amostragem dos dados deve ser de um segundo.
    3. Se o dado de entrada tiver passado por interpolação linear a aceleração máxima e as bandas ficarão erradas.
    """)

    uploaded_files = st.file_uploader("Escolha um ou mais arquivos CSV - no referencial da rampa (x, y, z)", accept_multiple_files=True)
    if uploaded_files is not None:
        # st.session_state.trajet = []
        file_names = []
        for uploaded_file in uploaded_files:
            # file_details = {"Filename":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
            # st.write(file_details)
            file_names.append(uploaded_file.name)        
            # st.session_state.trajet.append(read_csv_index(uploaded_file))
 
        # Criar um selectbox para selecionar o arquivo a ser analisado
        # st.write(file_names)
        selected_file = st.selectbox("Selecione um arquivo para analisar", file_names)
        
        # Encontrar o arquivo selecionado no arquivo carregado
        for uploaded_file in uploaded_files:            
            if uploaded_file.name == selected_file:
                # Ler o arquivo como DataFrame
                # df_enu_rampa = pd.read_csv(uploaded_file )
                df_enu_rampa = pd.read_csv(uploaded_file,
                                index_col=False ,
                                skip_blank_lines=True ,
                                skiprows=[0],
                                header=None ,
                                names=['x', 'y', 'z'])
                
                if len(df_enu_rampa.index)>2000 or tempo_amostra < 1:
                    st.warning('Se a amostragem tiver sido aumentada com interpolação linear o calculo fica comprometido', icon=cn.WARNING)
                st.write(f"Analisando o arquivo: {selected_file}, no referencial da rampa")
                # st.write(df_enu_rampa)
                reframpa = st.session_state.lc_df[st.session_state.lc_df['name'] == st.session_state.rampa].to_dict('records')[0]
                refsensor = st.session_state.lc_df[st.session_state.lc_df['name'] == st.session_state.sensor].to_dict('records')[0]
                if st.session_state.rampa == st.session_state.sensor:
                    st.warning("Sensor e rampa são o mesmo sistema de referência", icon=cn.WARNING)
                    df_enu_sensor = df_enu_rampa
                else:
                    df_enu_sensor = enu1_to_enu2(df_enu_rampa.to_numpy(), reframpa, refsensor)
                # st.write(df_enu_sensor)
                st.subheader('**Resultados:**')
                
                result_df = calculate_velocity_acceleration(df_enu_sensor, tempo_amostra, erro_angular, erro_distancia)
                st.dataframe(result_df)

                st.subheader('**Gráficos:**')
                plot_seq = [ 'X(m)', 'Y(m)', 'Z(m)', 'VX(m/s)', 'VY(m/s)', 'VZ(m/s)', 'AX(m/s²)', 'AY(m/s²)', 'AZ(m/s²)']
                plot_streamlit_plotly(result_df, plot_seq, titulo='Gráfico de coordenadas cartesianas')
                plot_seq = ['Az(rad)', 'El(rad)', 'd(m)','Vaz(rad/s)', 'Vel(rad/s)', 'Vr(m/s)', 'Aaz(rad/s²)', 'Ael(rad/s²)', 'Ar(m/s²)']
                plot_streamlit_plotly(result_df, plot_seq, titulo='Gráfico de coordenadas polares')
                plot_seq = ['BandaAq_Az(mrad/s²)','BandaAq_El(mrad/s²)','BandaAq_d(m/s²)',
                            'Banda_Az(mrad/s²)','Banda_El(mrad/s²)', 'Banda_d(m/s²)']
                plot_streamlit_plotly(result_df, plot_seq, titulo='Gráfico de Bandas de aquisição e de regime')




if __name__== '__main__':
    main()




# def plot_individual_graphs(df, plot_seq):
#     """
#     Gera 9 gráficos individuais para cada coluna do DataFrame fornecido, exceto a coluna de tempo ('Tempo (s)').

#     Args:
#         df (pd.DataFrame): DataFrame com as colunas a serem plotadas. Deve conter uma coluna 'Tempo (s)'.
#     """
#     plt.rcParams['axes.grid'] = True

#     # Configuração do layout 3x3
#     plt_m, plt_n = 3, 3
#     figure, axis = plt.subplots(plt_m, plt_n)

#     # # Determinar a sequência de colunas a serem plotadas (excluindo 'Tempo (s)')
#     # plot_seq = df.columns.difference(['TR(s)'])

#     # Garantir que o tamanho do plot seja compatível com a quantidade de dados
#     figure.set_size_inches(16, 8)

#     # Iterar sobre as subplots e as colunas
#     for i in range(plt_m):
#         for j in range(plt_n):
#             idx = plt_n * i + j
#             if idx < len(plot_seq):
#                 col_name = plot_seq[idx]
#                 axis[i, j].plot(df['TR(s)'], df[col_name], linewidth=0.6, color='r', label=col_name)
#                 axis[i, j].set_title(col_name, fontsize=10)
#                 axis[i, j].legend(fontsize=8)
#             else:
#                 # Remover eixos extras caso não haja mais colunas para plotar
#                 axis[i, j].axis('off')

#     # Ajustar espaçamento e exibir a figura
#     figure.tight_layout()
#     # Exibir o gráfico no Streamlit
#     st.pyplot(figure)