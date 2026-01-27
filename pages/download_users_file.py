
import streamlit as st
from pages.pull_users.horizon_client_table import horizon_clients

# Настройка Streamlit
st.set_page_config(page_title="Загрузка данных клиентов", layout="wide")

horizon_clients()
