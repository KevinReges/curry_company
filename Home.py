import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲')

# image_path = '/Users/kevin/Documents/repos/ftc/'
image = Image.open('logo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growdth Dashboard')

st.markdown(
    """
    Growdth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Resaturantes.
    ### Como utilizar esse  Growdth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
    - Time de Data Science no Discord
        @Kevin_Reges
    """ )