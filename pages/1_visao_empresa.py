import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide')

# -------------------------------
#         Funções
#--------------------------------

def order_metric( df1 ):
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        # grafico de barras
        figure = px.bar(df_aux, x= 'Order_Date', y= 'ID')
            
        return figure
    
def traffic_order_city(df1):
        cols = ['ID', 'City', 'Road_traffic_density']
        df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
        figure = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
                
        return figure    
    
    
def traffic_order_share(df1):
    
    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    # calculo da porcentagem
    df_aux['entregas_porc'] = df_aux['ID'] / df_aux['ID'].sum()
    figure = px.pie(df_aux, values='entregas_porc', names='Road_traffic_density')
    return figure    


def order_by_week(df1):
    # criar coluna de semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'Week_of_year']
    df_aux = df1.loc[:, cols].groupby('Week_of_year').count().reset_index()
    # desenhar grafico linhas
    figure = px.line(df_aux, x='Week_of_year', y='ID')
    
    return figure


def order_share_by_week(df1):

    cols01 = ['ID', 'Week_of_year']
    df_aux1 = df1.loc[:, cols01].groupby('Week_of_year').count().reset_index()
    cols02 = ['Delivery_person_ID', 'Week_of_year']
    df_aux02 = df1.loc[:, cols02].groupby('Week_of_year').nunique().reset_index()
    # juntar df_aux01 + df_aux02    
    df_aux = pd.merge(df_aux1, df_aux02, how='inner')
    # divisao
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    figure = px.line(df_aux, x='Week_of_year', y='Order_by_delivery')
            
    return figure


def country_maps(df1):
    
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)     
        
    return None


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



st.header('Marketplace - Visão Cliente')

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

st.sidebar.markdown("""___""")


traffic_options = st.sidebar.multiselect(
    'Condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

# Filtro por Data
select_lines = df1['Order_Date'] < date_slider
df1 = df1.loc[select_lines, :]

# Filtro por transito
select_lines = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[select_lines, :]


st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')



# =====================================================
#              Layout no Streamilit
# =====================================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# Quantidade pedidos por linha
with tab1:
    
    with st.container():
        # Order Metric
        figure = order_metric( df1 )
        st.markdown('# Orders by Day')
        st.plotly_chart(figure, use_container_width=True)
        
      
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            
            st.header('Traffic Order share')
            figure = traffic_order_share( df1 )
            st.plotly_chart(figure, use_container_width=True)
            
         
        with col2:
            
            st.header('Traffic Order City')
            figure = traffic_order_city(df1)
            st.plotly_chart(figure, use_container_width=True)
            

with tab2:
    
    with st.container():
        
        st.markdown('# Order by Week')
        figure = order_by_week(df1)
        st.plotly_chart(figure, use_container_width=True)
        

    
    with st.container():
    
        st.markdown('# Order Share by Week')
        figure = order_share_by_week(df1)
        st.plotly_chart(figure, use_container_width=True)
            
            
        
       
    
with tab3:
    
    st.markdown('# Country Maps')
    country_maps(df1)
    
    





