import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')

# -------------------------------
#         Funções
#--------------------------------

def top_delivers(df1, top_asc):
    cols = ['Delivery_person_ID', 'City','Time_taken(min)']

    df2 = (df1.loc[:, cols].groupby(['City','Delivery_person_ID'])
                            .mean()
                            .sort_values(['City','Time_taken(min)'],ascending=top_asc)
                            .reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
    
    return df3



def clean_code( df1 ):
    
   
    """  Esta funcao tem a responsabilidade de limpar o dataframe
         Tipos de limpezas:
         1. Remoção dos espaços das variáveis de texto
         2. Remoção dos dados NaN
         3. Mudança do tipo de coluna
         4. Formatação da coluna de datas
         5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )
         
         Imput: Dataframe
         Output: Dataframe
    """

    # Remover espaços dentro de strings/ texto/ objeto

    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery-person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'Delivery_person_Age'] = df1.loc[:, 'Delivery_person_Age'].str.strip()
    df1.loc[:, 'multiple_deliveries'] = df1.loc[:, 'multiple_deliveries'].str.strip()

    # Remover NaN de colunas

    select_line = df1.loc[:, 'Delivery_person_Age'] != 'NaN'
    df1 = df1.loc[select_line, :].copy()

    select_line = df1.loc[:, 'Road_traffic_density'] != 'NaN'
    df1 = df1.loc[select_line, :].copy()

    select_line = df1.loc[:, 'City'] != 'NaN'
    df1 = df1.loc[select_line, :].copy()

    select_line = df1.loc[:, 'multiple_deliveries'] != 'NaN'
    df1 = df1.loc[select_line, :].copy()

    select_line = df1.loc[:, 'Festival'] != 'NaN'
    df1 = df1.loc[select_line, :].copy()

    # Coverter texto para numero

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)


    # Converter Coluna Order_date de texto para data

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Limando Colunaastype(int) Time_taken(min):

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)']

    return df1

# ------------------------ Inicio da Estrutura lógica do código -------------------------

# ---------------------------------
# Import dataset
# ----------------------------------
df = pd.read_csv('dataset/train.csv')

# ---------------------------------
# Limpando os dados
# ----------------------------------
df1 = clean_code(df )



# =====================================================
#              Barra Lateral
# =====================================================



st.header('Marketplace - Visão Entregadores')

#image_path = 'logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value= pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format= 'DD-MM-YYYY')

# Filtro por Data
select_lines = df1['Order_Date'] < date_slider
df1 = df1.loc[select_lines, :]


st.sidebar.markdown("""___""")


traffic_options = st.sidebar.multiselect(
    'Condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

# Filtro por transito
select_lines = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[select_lines, :]



weather_options = st.sidebar.multiselect(
        'Condições de Clima',
         ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 
          'conditions Sunny', 'conditions Windy'],
         default = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 
                    'conditions Sunny', 'conditions Windy'] )

    
 # Filtro por Clima
select_lines = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[select_lines, :]




st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')





# =====================================================
#              Layout no Streamilit
# =====================================================


tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            # Maior idade dos entregadores
            
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            # Menor idade dos entregadore
            
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # Melhor condiçao de veiculo
            
            melhor = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor)

            
        with col4:
            # Pior condição de veículo
        
            pior = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior)
            
    with st.container():
        st.markdown( """---""" )
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por Entregador')
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            avg_rating_delivery = df1.loc[:, cols].groupby('Delivery_person_ID').mean().reset_index()
            
            st.dataframe(avg_rating_delivery)
            
        with col2:
            
            st.markdown('##### Avaliação media por Trafego')
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']

            df_avg_std_traffic = (df1.loc[:, cols].groupby('Road_traffic_density')
                                                  .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ) )

            # mundanca nome das colunas
            df_avg_std_traffic.columns = ['Delivery_mean', 'Delivery_std']

            # reset index

            df_avg_std_traffic = df_avg_std_traffic.reset_index()

            st.dataframe( df_avg_std_traffic)

            
            
            st.markdown('##### Avaliação media por Clima')
            
            cols = ['Delivery_person_Ratings', 'Weatherconditions']

            df_avg_std_weather = (df1.loc[:, cols].groupby('Weatherconditions')
                                                  .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ))

            # mudar nome colunas
            df_avg_std_weather.columns = ['Delivey_mean', 'Delivery_std']

            # resetar index
            df_avg_std_weather = df_avg_std_weather.reset_index()
            
            st.dataframe(df_avg_std_weather)
            
            
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top Entregadores mais rapidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
            

        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            