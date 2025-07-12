import streamlit as st
from streamlit import session_state as state

st.set_page_config(
    page_title="Demonstração do case Titanic",
    page_icon=":ship:",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("Menu")
# grava a url e api key na sessão
state.url = st.sidebar.text_input("URL da API", "http://localhost:8000")
state.api_key = st.sidebar.text_input("API Key", type="password")
