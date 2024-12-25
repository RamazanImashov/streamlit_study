import requests
import streamlit as st
from typing import List, Dict, Optional
from config import (
    DEFAULT_API,
    WAREHOUSE_API_URL,
    CLIENT_API_URL,
    DRF_API_URL_FILE,
    SOCIAL_MEDIA_API_URL,
    CONTACT_API_URL,
    ORDER_API,
)


@staticmethod
def get_warehouse_data(params=None) -> List[Dict]:
    try:
        response = requests.get(DEFAULT_API+WAREHOUSE_API_URL, params=params)
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        st.error(f"Не удалось получить данные о складах: {e}")
        return []


@staticmethod
def get_clients(params=None) -> List[Dict]:
    try:
        response = requests.get(DEFAULT_API+CLIENT_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Не удалось получить данные клиентов: {e}")
        return []


@staticmethod
def get_contacts(params=None) -> List[Dict]:
    try:
        response = requests.get(DEFAULT_API+CONTACT_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Не удалось получить данные контактов: {e}")
        return []


@staticmethod
def get_social_media(params=None) -> List[Dict]:
    try:
        response = requests.get(DEFAULT_API+SOCIAL_MEDIA_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Не удалось получить данные социальных сетей: {e}")
        return []


@staticmethod
def get_from_api_orders(params=None):
    try:
        response = requests.get(DEFAULT_API+ORDER_API, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ошибка при запросе к API: {e}")
        return []


@staticmethod
def get_from_api_order_id(id, params=None):
    try:
        response = requests.get(DEFAULT_API+ORDER_API+id, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ошибка при запросе к API: {e}")
        return []


@staticmethod
def post_to_api_order(data):
    try:
        response = requests.post(DEFAULT_API+ORDER_API, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ошибка при отправке данных в API: {e}")
        return None


@staticmethod
def delete_to_api_order(id, data):
    try:
        response = requests.delete(DEFAULT_API+ORDER_API+id, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ошибка при отправке данных в API: {e}")
        return None