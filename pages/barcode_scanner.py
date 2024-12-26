import streamlit as st
from pages.barcoder.get_and_delete import delete_order, get_order
from pages.barcoder.add_upload import upload_excel_order, add_order
from pages.barcoder.scan_and_comparison import scan_by_image, scan_by_camera

# Настройка Streamlit
st.set_page_config(page_title="Логистическая платформа", layout="wide")


# Выбор страницы
page = st.sidebar.selectbox("Навигация", [
    "Обзор базы и Удаление записей", "Добавить данные и Загрузка Excel",
    "Сканирование и сравнение"])

if page == "Обзор базы и Удаление записей":
    get_order(), delete_order()

elif page == "Добавить данные и Загрузка Excel":
    upload_excel_order(), add_order()

elif page == "Сканирование и сравнение":
    scan_by_image(), scan_by_camera()
