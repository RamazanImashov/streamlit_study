
import streamlit as st
from pages.pull_users.dordoi_client_table import dordoi_clients

st.set_page_config(page_title="Загрузка данных клиентов", layout="wide")

dordoi_clients()

