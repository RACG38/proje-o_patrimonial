import streamlit as st



#Página
cor_fundo_pagina = "#120c2b"
cor_texto_pagina = "#FFFFFF"

#Sidebar
cor_sidebar = "#000000"
cor_elementos_sidebar = "#000000"
cor_texto_sidebar = "#FFFFFF"

#Tabela
cor_fundo_tabela = "#000000"
cor_texto_tabela = "#FFFFFF"




def streamlit_page_config():
    st.set_page_config(
        page_title="Projeção de Investimentos",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def streamlit_css():   

    # Inserir o CSS personalizado para alterar as cores de fundo
    st.markdown(
        f"""
        <style>
        /* Cor de fundo do corpo da página */
        .stApp {{
            background-color: {cor_fundo_pagina}; 
            color: {cor_texto_pagina}; /* Cor do texto escura */
        }}

        /* Cor de fundo do sidebar */
        .css-1d391kg {{ 
            background-color: {cor_sidebar}; /* Cor de fundo branca para o sidebar */
            color: {cor_texto_sidebar}; /* Cor do texto escura */
        }}

        /* Cor de fundo dos widgets do sidebar */
        .css-1d391kg .st-bk {{
            background-color: {cor_elementos_sidebar}; /* Cor de fundo muito clara para widgets */
        }}

        /* Ajusta a largura do sidebar */
        .css-1d391kg {{
            max-width: 300px; /* Ajuste a largura máxima conforme necessário */
        }}

        /* Adiciona bordas e sombras aos widgets para um visual mais moderno */
        .stButton, .stTextInput, .stSelectbox, .stMultiselect {{
            border-radius: 8px; /* Cantos arredondados */
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Sombra suave */
        }}

        /* Adiciona uma cor de fundo e ajuste nas tabelas */
        .stDataFrame {{
            background-color: {cor_sidebar}; /* Cor de fundo branca para tabelas */
            border-radius: 8px; /* Cantos arredondados */
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); /* Sombra suave */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )