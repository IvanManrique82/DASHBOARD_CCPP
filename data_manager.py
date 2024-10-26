import pandas as pd
import streamlit as st

@st.cache
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

@st.cache
def load_usuarios(file_path):
    usuarios = pd.read_excel(file_path)
    return usuarios
