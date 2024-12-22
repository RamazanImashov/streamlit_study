import streamlit as st
from pymongo import MongoClient
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["logistics"]
collection = db["shipments"]

# Настройка Streamlit
st.set_page_config(page_title="Логистическая платформа", layout="wide")

# Выбор страницы
page = st.sidebar.selectbox("Навигация", ["Обзор базы", "Добавить данные", "Сканирование и сравнение", "Загрузка фото", "Удаление записей"])

if page == "Обзор базы":
    st.title("Обзор базы данных")

    # Загрузка данных из MongoDB
    data = list(collection.find())
    for entry in data:
        entry["_id"] = str(entry["_id"])  # Преобразуем ObjectId в строку для отображения
    df = pd.DataFrame(data)

    # Отображение данных
    st.dataframe(df)

elif page == "Добавить данные":
    st.title("Добавить данные в базу")

    # Форма для добавления данных
    with st.form("add_shipment"):
        track_code = st.text_input("Трек-код")
        client_code = st.text_input("Клиентский код")
        description = st.text_area("Описание", placeholder="Введите описание груза...")
        submitted = st.form_submit_button("Добавить")

    if submitted:
        # Сохранение данных в MongoDB
        if track_code and client_code:
            collection.insert_one({"track_code": track_code, "client_code": client_code, "description": description})
            st.success("Данные успешно добавлены!")
        else:
            st.error("Пожалуйста, заполните все обязательные поля.")

elif page == "Сканирование и сравнение":
    st.title("Сканирование и сравнение")

    # Инструкция для пользователя
    st.info(
        "Для использования камеры:\n"
        "1. Убедитесь, что вы предоставили разрешение на использование камеры в вашем браузере.\n"
        "2. Если браузер запросил доступ, подтвердите его.\n"
        "3. Убедитесь, что устройство оснащено рабочей камерой."
    )

    # Проверка наличия камеры
    enable = st.checkbox("Включить камеру")
    if not enable:
        st.warning("Камера отключена. Включите камеру для сканирования.")
    else:
        picture = st.camera_input("Take a picture", disabled=not enable)

        if picture:
            st.image(picture, caption="Ваш снимок")
            # Декодирование QR или штрих-кода
            image = Image.open(BytesIO(picture.getvalue()))
            decoded_objects = decode(image)

            if decoded_objects:
                for obj in decoded_objects:
                    track_code = obj.data.decode("utf-8")
                    st.write(f"Распознанный трек-код: {track_code}")

                    # Поиск в базе данных
                    shipment = collection.find_one({"track_code": track_code})
                    if shipment:
                        shipment["_id"] = str(shipment["_id"])
                        st.write("Информация о грузе:", shipment)
                    else:
                        st.warning("Данные по этому трек-коду не найдены.")
            else:
                st.error("QR или штрих-код не распознан.")

elif page == "Загрузка фото":
    st.title("Загрузка фото для обработки")

    # Форма для загрузки изображения
    uploaded_file = st.file_uploader("Загрузите изображение с QR или штрих-кодом", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="Загруженное изображение")

        # Декодирование QR или штрих-кода
        image = Image.open(uploaded_file)
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                track_code = obj.data.decode("utf-8")
                st.write(f"Распознанный трек-код: {track_code}")

                # Поиск в базе данных
                shipment = collection.find_one({"track_code": track_code})
                if shipment:
                    shipment["_id"] = str(shipment["_id"])
                    st.write("Информация о грузе:", shipment)
                else:
                    st.warning("Данные по этому трек-коду не найдены.")
        else:
            st.error("QR или штрих-код не распознан.")

elif page == "Удаление записей":
    st.title("Удаление записей из базы данных")

    # Загрузка данных из MongoDB
    data = list(collection.find())
    for entry in data:
        entry["_id"] = str(entry["_id"])  # Преобразуем ObjectId в строку для отображения
    df = pd.DataFrame(data)

    # Отображение данных
    st.dataframe(df)

    # Удаление записи
    track_code_to_delete = st.text_input("Введите трек-код для удаления")
    if st.button("Удалить запись"):
        result = collection.delete_one({"track_code": track_code_to_delete})
        if result.deleted_count > 0:
            st.success("Запись успешно удалена!")
        else:
            st.error("Запись с указанным трек-кодом не найдена.")
