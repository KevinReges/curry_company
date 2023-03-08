import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import numpy as np
import pandas as pd

st.set_page_config( page_title='Visão Resaturantes', page_icon='🍽️', layout='wide')

#-------------------------------------
#         Funções
#-------------------------------------


# harvesine -> calcular distancia entre dois locais:
# haversine ( ('Restaurant_latitude', 'Restaurant_longitude'), ('Delivery_location_latitude',
                                                                #'Delivery_location_longitude') )
def distance(df1, grafico):

    
    if grafico == False:        
    
        # calcular distancia em todas as linhas:

        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance(km)'] = df1.loc[:, cols].apply(lambda x:
        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'],
                                                                           x['Delivery_location_longitude'])), axis=1 )

        # np.round = formatar numeros decimais
        avg_distance = np.round( df1['Distance(km)'].mean(), 1)

        return avg_distance
    
    else:

        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df1['Distance(km)'] = df1.loc[:, cols].apply(lambda x:
                       haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], 
                                                                                          x['Delivery_location_longitude'])), axis=1 )

        avg_distance = df1.loc[:, ['City', 'Distance(km)']].groupby( 'City' ).mean().reset_index()
        # pull fração do raio da pizza
        
        grafico = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['Distance(km)'], pull=[0, 0.1, 0] ) ] )
        
        return grafico
#-----------------------------------------------------------------------------------------------------------

def avg_std_time_orders(df1, festival, op):
    cols = ['Time_taken(min)', 'Festival']

    df_aux = np.round( df1.loc[:, cols].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']} ), 1)
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    select_line = df_aux['Festival'] == festival
    df_aux = df_aux.loc[select_line, op]
            
    return df_aux

#---------------------------------------------------------------------------------------------------------------

def avg_std_time_graph(df1):
    
    # agg( {'chave': 'valor'} ) 
    cols = ['Time_taken(min)', 'City']

    df_aux = df1.loc[:, cols].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    grafico = go.Figure()
    grafico.add_trace( go.Bar( name='Control',  x=df_aux['City'], y=df_aux['avg_time'],
                                             error_y=dict( type='data', array=df_aux['std_time'])))
    grafico.update_layout(barmode='group')
            
    return grafico

#--------------------------------------------------------------------------------------------------

def avg_std_city_traffic_graph(df1):
            
        
        cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} )
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        grafico = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                 color='std_time', color_continuous_scale='RdBu',
                                 color_continuous_midpoint=np.average(df_aux['std_time']))
        return grafico
#--------------------------------------------------------------------------------------------------


def clean_code(df1):

    # Remover espaços dentro de strings/ texto/ objeto

    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery-person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    df1.loc[:, 'multiple_deliveries'] = df1.loc[:, 'multiple_deliveries'].str.strip()


    # Remover NaN de colunas

    select_line = df1.loc[:, 'Delivery_person_Ratings'] != 'NaN '

    select_line = df1.loc[:, 'Delivery_person_Age'] != 'NaN '
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

    # Limando Coluna Time_taken(min):

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)



# =====================================================
#              Barra Lateral
# =====================================================



st.header('Marketplace - Visão Restaurantes')

# image_path = 'logo.png'
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


st.sidebar.markdown("""___""")
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

city_options = st.sidebar.multiselect(
    'Tipos de cidades',
    ['Urban', 'Semi-Urban', 'Metropolitian'],
    default = ['Urban', 'Semi-Urban', 'Metropolitian'])

# Filtro por cidade
select_lines = df1['City'].isin(city_options)
df1 = df1.loc[select_lines, :]


st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')





# =====================================================
#              Layout no Streamilit
# =====================================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    
    with st.container():
        
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            
            qtd_entregadores = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', qtd_entregadores)
            
        with col2:
            
            avg_distance = distance(df1, grafico=False)
            col2.metric('Distância média das entregas', avg_distance)
            
        with col3:
            
            df_aux = avg_std_time_orders(df1, 'Yes', 'avg_time')
            col3.metric('Tempo medio de entrega c/ Festival', df_aux)
            
        with col4:
            
            df_aux = avg_std_time_orders(df1, 'Yes', 'std_time')
            col4.metric('Desvio Padrão de entrega c/ Festival', df_aux)
            
        with col5:
            
            df_aux = avg_std_time_orders(df1, 'No', 'avg_time')
            col5.metric('Tempo medio de entrega s/ Festival', df_aux)
            
        with col6:    
            
            df_aux = avg_std_time_orders(df1, 'No', 'std_time')
            col6.metric('Desvio padrão de entrega s/ Festival', df_aux)
            
    with st.container():
        st.markdown("""___""")
        st.markdown('### Tempo por Cidade e Tipo de Pedido')
        
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            # grafico barras com marcador std
            grafico = avg_std_time_graph(df1)
            st.plotly_chart(grafico, use_container_width=True)
            
        with col2:    
        
            cols = ['Time_taken(min)', 'City', 'Type_of_order']

            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg( { 'Time_taken(min)': ['mean', 'std'] } )

            df_aux.columns = ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width=True)
        
        
            
    with st.container():
        st.markdown("""___""")
            
        st.markdown('#### Tempo medio de entrega p/cidade')
        # grafico pizza que puxa
          
        grafico = distance(df1, grafico=True)    
        st.plotly_chart(grafico)       
                                      
            
        with st.container():
            
            st.markdown("""___""")
            st.markdown('#### Desvio Padrão e Média por Cidade e Tráfego')
                
            grafico = avg_std_city_traffic_graph(df1)
            st.plotly_chart(grafico)
        

       
        
        
        

        
        
        
