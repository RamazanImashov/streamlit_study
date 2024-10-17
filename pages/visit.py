import streamlit as st
import requests
from decouple import config

# Адрес API DRF
API_URL = config("DRF_API_URL_FILE")  # Замените на ваш адрес API

DRF_API_URL = config("DRF_API_URL")


# Получение списка клиентов и файлов через API DRF
def get_files():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Не удалось получить данные с API")
        return []


# Интерфейс Streamlit
st.title("Файлы клиентов")

# Получаем файлы через API
files = get_files()

if files:
    for file in files:
        st.write(f"Клиент: {file['client_name']['username']}")
        st.write(f"Файл: {file['file_path']}")
        st.write(f"Дата создания: {file['created_at']}")

        # Кнопка для скачивания файла
        file_url = f"{DRF_API_URL}{file['file_path']}"  # Генерация полного пути
        st.write(f"[Скачать файл]({file_url})")

# Загрузка нового файла
uploaded_file = st.file_uploader("Загрузите файл", type=['png'])
if uploaded_file is not None:
    files = {'file': uploaded_file.getvalue()}
    client_id = st.text_input("Введите ID клиента")
    if client_id and st.button("Отправить файл"):
        response = requests.post(API_URL, files=files, data={'client_name': client_id})
        if response.status_code == 201:
            st.success("Файл успешно загружен!")
        else:
            st.error("Ошибка при загрузке файла.")
