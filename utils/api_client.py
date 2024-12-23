import requests
import streamlit as st
from typing import List, Dict, Optional


class APIClient:
    def __init__(self, warehouse_url: str, client_url: str, contact_url: str, social_media_url: str):
        self.warehouse_url = warehouse_url
        self.client_url = client_url
        self.contact_url = contact_url
        self.social_media_url = social_media_url

    def get_warehouse_data(self) -> List[Dict]:
        try:
            response = requests.get(self.warehouse_url)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            st.error(f"Не удалось получить данные о складах: {e}")
            return []

    def get_clients(self) -> List[Dict]:
        try:
            response = requests.get(self.client_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Не удалось получить данные клиентов: {e}")
            return []

    def get_contacts(self) -> List[Dict]:
        try:
            response = requests.get(self.contact_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Не удалось получить данные контактов: {e}")
            return []

    def get_social_media(self) -> List[Dict]:
        try:
            response = requests.get(self.social_media_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Не удалось получить данные социальных сетей: {e}")
            return []
