# utils/get_contact.py
import streamlit as st
import requests
from decouple import config


def get_contacts():
    url = config("CONTACT_API_URL")
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Не удалось получить контактные данные.")
        return []


