import streamlit as st
import requests
from decouple import config


def get_warehouse_data():
    url = config("WAREHOUSE_API_URL")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        st.error("Не удалось получить данные о складах.")
        return []