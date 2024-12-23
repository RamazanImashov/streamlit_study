import streamlit as st
from pymongo import MongoClient
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import pyheif

# Подключение к MongoDB
client = MongoClient("mongodb://mongodb:27017")
db = client["logistics"]
collection = db["shipments"]

# Настройка Streamlit
st.set_page_config(page_title="Логистическая платформа", layout="wide")

# Выбор страницы
page = st.sidebar.selectbox("Навигация", [
    "Обзор базы и Удаление записей", "Добавить данные и Загрузка Excel",
    "Сканирование и сравнение"])

if page == "Обзор базы и Удаление записей":
    st.title("Обзор базы данных")

    # Загрузка данных из MongoDB
    data = list(collection.find({}, {"_id": 0}))  # Исключаем поле _id
    df = pd.DataFrame(data)

    # Группировка данных по дате добавления
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
        selected_date = st.date_input("Выберите дату", value=pd.Timestamp.now().date())
        filtered_data = df[df["created_at"].dt.date == selected_date]
        st.subheader(f"Грузы за {selected_date}")
        st.dataframe(filtered_data)

        # Скачивание таблицы в Excel
        if not filtered_data.empty:
            excel_file = filtered_data.to_excel(index=False, engine="openpyxl")
            st.download_button(
                label="Скачать таблицу в Excel",
                data=excel_file,
                file_name=f"shipments_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.dataframe(df)

    st.title("Удаление записей из базы данных")

    # Удаление записи
    track_code_to_delete = st.text_input("Введите трек-код для удаления")
    if st.button("Удалить запись"):
        result = collection.delete_one({"track_code": track_code_to_delete})
        if result.deleted_count > 0:
            st.success("Запись успешно удалена!")
        else:
            st.error("Запись с указанным трек-кодом не найдена.")

elif page == "Добавить данные и Загрузка Excel":
    st.title("Загрузка Excel в базу данных")

    # Форма для загрузки Excel
    uploaded_excel = st.file_uploader("Загрузите Excel-файл", type=["xlsx", "xls"])

    if uploaded_excel:
        try:
            df = pd.read_excel(uploaded_excel)

            # Преобразование track_code в строку
            df["track_code"] = df["track_code"].astype(str)

            # Проверка необходимых колонок
            if not {"track_code", "client_code"}.issubset(df.columns):
                st.error("Excel файл должен содержать колонки 'track_code' и 'client_code'")
            else:
                # Добавление данных в MongoDB
                for _, row in df.iterrows():
                    collection.insert_one({
                        "track_code": row["track_code"],
                        "client_code": row["client_code"],
                        "description": row.get("description", ""),
                        "created_at": pd.Timestamp.now(),
                        "arrived": False,
                        "issued": False
                    })
                st.success("Данные из Excel успешно загружены в базу!")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")

    st.title("Добавить данные в базу")

    # Форма для добавления данных
    with st.form("add_shipment"):
        track_code = st.text_input("Трек-код")
        client_code = st.text_input("Клиентский код")
        description = st.text_area("Описание", placeholder="Введите описание груза...")
        arrived = st.checkbox("Груз прибыл")
        issued = st.checkbox("Груз выдан")
        submitted = st.form_submit_button("Добавить")

    if submitted:
        # Сохранение данных в MongoDB
        if track_code and client_code:
            collection.insert_one({
                "track_code": track_code,
                "client_code": client_code,
                "description": description,
                "created_at": pd.Timestamp.now(),
                "arrived": arrived,
                "issued": issued
            })
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

    # Сканирование через камеру
    st.header("Сканирование через камеру")
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

                        # Обновление состояния груза
                        with st.form(f"update_status_{track_code}"):
                            arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                            issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                            update_submitted = st.form_submit_button("Обновить статус")

                        if update_submitted:
                            collection.update_one(
                                {"track_code": track_code},
                                {"$set": {"arrived": arrived, "issued": issued}}
                            )
                            st.success("Статус груза обновлен!")
                    else:
                        st.warning("Данные по этому трек-коду не найдены.")
            else:
                st.error("QR или штрих-код не распознан.")

    # Сканирование через загрузку изображения
    st.header("Сканирование через загрузку изображения")
    uploaded_file = st.file_uploader("Загрузите изображение с QR или штрих-кодом", type=["png", "jpg", "jpeg", "heic"])

    if uploaded_file:
        # Конвертация HEIC в JPEG
        if uploaded_file.name.endswith(".heic"):
            heif_file = pyheif.read(uploaded_file.getvalue())
            image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
        else:
            image = Image.open(uploaded_file)

        st.image(image, caption="Загруженное изображение")

        # Декодирование QR или штрих-кода
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

                    # Обновление состояния груза
                    with st.form(f"update_status_{track_code}_file"):
                        arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                        issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                        update_submitted = st.form_submit_button("Обновить статус")

                    if update_submitted:
                        collection.update_one(
                            {"track_code": track_code},
                            {"$set": {"arrived": arrived, "issued": issued}}
                        )
                        st.success("Статус груза обновлен!")
                else:
                    st.warning("Данные по этому трек-коду не найдены.")
        else:
            st.error("QR или штрих-код не распознан.")
