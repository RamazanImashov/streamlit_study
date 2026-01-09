
import streamlit as st
from pages.pull_users.dordoi_client_table import dordoi_clients
from pages.pull_users.horizon_client_table import horizon_clients

# Настройка Streamlit
st.set_page_config(page_title="Загрузка данных клиентов", layout="wide")


# Выбор страницы
page = st.sidebar.selectbox("Навигация", [
    "Загрузка данных ТАБУЛАН", "Загрузка данных ГОРИЗОНТ"
])

if page == "Загрузка данных ТАБУЛАН":
    dordoi_clients()

elif page == "Загрузка данных ГОРИЗОНТ":
    horizon_clients()
