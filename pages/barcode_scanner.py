import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime
from utils.api_client import get_from_api_orders, post_to_api_order, delete_to_api_order, patch_to_api_order

# Настройка Streamlit
st.set_page_config(page_title="Логистическая платформа", layout="wide")


# Функция для преобразования формата даты и времени
def format_datetime(value):
    return value.strftime('%d.%m.%Y %H:%M:%S')


# Выбор страницы
page = st.sidebar.selectbox("Навигация", [
    "Обзор базы и Удаление записей", "Добавить данные и Загрузка Excel",
    "Сканирование и сравнение"])

if page == "Обзор базы и Удаление записей":
    st.title("Обзор базы данных")

    # Загрузка данных из API
    data = get_from_api_orders()
    df = pd.DataFrame(data)

    # Преобразование формата даты
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["created_at"] = df["created_at"].apply(format_datetime)

        selected_date = st.date_input("Выберите дату", value=datetime.now().date())
        filtered_data = df[pd.to_datetime(df["created_at"]).dt.date == selected_date]
        st.subheader(f"Грузы за {selected_date}")
        st.dataframe(filtered_data)

        # Скачивание таблицы в Excel
        if not filtered_data.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                filtered_data.to_excel(writer, index=False, sheet_name="Грузы")
            output.seek(0)

            st.download_button(
                label="Скачать таблицу в Excel",
                data=output,
                file_name=f"Грузы_{selected_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.dataframe(df)

    st.title("Удаление записей из базы данных")

    # Удаление записи
    track_code_to_delete = st.text_input("Введите трек-код для удаления")
    order_id_form_track_code = get_from_api_orders(f"?search={track_code_to_delete}")
    if st.button("Удалить запись"):
        delete_to_api_order(order_id_form_track_code[0][1], {})
        st.success("Запись успешно удалена!")

elif page == "Добавить данные и Загрузка Excel":
    st.title("Загрузка Excel в базу данных")

    # Форма для загрузки Excel
    uploaded_excel = st.file_uploader("Загрузите Excel-файл", type=["xlsx", "xls"])

    if uploaded_excel:
        try:
            df = pd.read_excel(uploaded_excel)

            # Преобразование колонок на русский
            column_mapping = {
                "track_code": "Трек-код",
                "client_code": "Код клиента",
                "description": "Описание"
            }
            df.rename(columns=column_mapping, inplace=True)

            # Преобразование track_code и client_code в строку и удаление пробелов
            df["Трек-код"] = df["Трек-код"].astype(str).str.replace(" ", "")
            df["Код клиента"] = df["Код клиента"].astype(str).str.replace(" ", "")

            # Проверка необходимых колонок
            if not {"Трек-код", "Код клиента"}.issubset(df.columns):
                st.error("Excel файл должен содержать колонки 'Трек-код' и 'Код клиента'")
            else:
                # Добавление данных через API
                for _, row in df.iterrows():
                    post_to_api_order({
                        "track_code": row["Трек-код"],
                        "client_code": row["Код клиента"],
                        "description": row.get("Описание", "")
                    })
                st.success("Данные из Excel успешно загружены в базу!")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")

    st.title("Добавить данные в базу")

    # Форма для добавления данных
    with st.form("add_shipment"):
        track_code = st.text_input("Трек-код")
        client_code = st.text_input("Код клиента")
        description = st.text_area("Описание", placeholder="Введите описание груза...")
        submitted = st.form_submit_button("Добавить")

    if submitted:
        # Сохранение данных через API
        if track_code and client_code:
            post_to_api_order({
                "track_code": track_code.replace(" ", ""),
                "client_code": client_code.replace(" ", ""),
                "description": description
            })
            st.success("Данные успешно добавлены!")
        else:
            st.error("Пожалуйста, заполните все обязательные поля.")

elif page == "Сканирование и сравнение":
    st.title("Сканирование и сравнение")

    # Сканирование через загрузку изображения
    st.header("Сканирование через загрузку изображения")
    uploaded_file = st.file_uploader("Загрузите изображение с QR или штрих-кодом", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Загруженное изображение")

        # Декодирование QR или штрих-кода
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                track_code = obj.data.decode("utf-8").replace(" ", "")
                st.write(f"Распознанный трек-код: {track_code}")

                # Поиск в базе данных через API
                shipment = get_from_api_orders(f"?search={track_code}")

                if shipment:
                    shipment_display = {
                        "Трек-код": shipment["track_code"],
                        "Клиент": shipment["client_name"],
                        "Описание": shipment["description"],
                        "Дата добавления": format_datetime(pd.to_datetime(shipment["created_at"])),
                        "Прибыл": "Да" if shipment["arrived"] else "Нет",
                        "Выдан": "Да" if shipment["issued"] else "Нет"
                    }
                    st.write("Информация о грузе:", shipment_display)

                    # Обновление состояния груза
                    with st.form(f"update_status_{track_code}_file"):
                        arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                        issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                        update_submitted = st.form_submit_button("Обновить статус")

                    if update_submitted:
                        order_id_form_track_code = get_from_api_orders(f"?search={track_code}")
                        patch_to_api_order(order_id_form_track_code[0][1], {
                            "arrived": arrived,
                            "issued": issued
                        })
                        st.success("Статус груза обновлен!")
                else:
                    st.warning("Данные по этому трек-коду не найдены.")
        else:
            st.error("QR или штрих-код не распознан.")
