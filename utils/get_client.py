import streamlit as st
import requests
from decouple import config


def get_clients():
    url = config("CLIENT_API_URL")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Не удалось получить данные клиентов.")
        return []