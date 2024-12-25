import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import pyheif
from cachetools import TTLCache, cached
from datetime import datetime

# Инициализация соединения с PostgreSQL через Streamlit
conn = st.connection("postgresql", type="sql")

# Кэш для ускорения работы
cache = TTLCache(maxsize=100, ttl=300)

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

    # Загрузка данных из PostgreSQL с кэшированием
    @cached(cache)
    def fetch_all_shipments():
        return conn.query("SELECT * FROM shipments", ttl="10m")

    data = fetch_all_shipments()
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
    if st.button("Удалить запись"):
        conn.execute("DELETE FROM shipments WHERE track_code = :track_code", {"track_code": track_code_to_delete})
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
                # Добавление данных в PostgreSQL
                for _, row in df.iterrows():
                    conn.execute(
                        """
                        INSERT INTO shipments (track_code, client_code, description, created_at, arrived, issued)
                        VALUES (:track_code, :client_code, :description, NOW(), :arrived, :issued)
                        """,
                        {
                            "track_code": row["Трек-код"],
                            "client_code": row["Код клиента"],
                            "description": row.get("Описание", ""),
                            "arrived": False,
                            "issued": False
                        }
                    )
                st.success("Данные из Excel успешно загружены в базу!")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")

    st.title("Добавить данные в базу")

    # Форма для добавления данных
    with st.form("add_shipment"):
        track_code = st.text_input("Трек-код")
        client_code = st.text_input("Код клиента")
        description = st.text_area("Описание", placeholder="Введите описание груза...")
        arrived = st.checkbox("Груз прибыл")
        issued = st.checkbox("Груз выдан")
        submitted = st.form_submit_button("Добавить")

    if submitted:
        # Сохранение данных в PostgreSQL
        if track_code and client_code:
            conn.execute(
                """
                INSERT INTO shipments (track_code, client_code, description, created_at, arrived, issued)
                VALUES (:track_code, :client_code, :description, NOW(), :arrived, :issued)
                """,
                {
                    "track_code": track_code.replace(" ", ""),
                    "client_code": client_code.replace(" ", ""),
                    "description": description,
                    "arrived": arrived,
                    "issued": issued
                }
            )
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
                track_code = obj.data.decode("utf-8").replace(" ", "")
                st.write(f"Распознанный трек-код: {track_code}")

                # Поиск в базе данных
                result = conn.query("SELECT * FROM shipments WHERE track_code = :track_code", {"track_code": track_code})
                shipment = result[0] if result else None

                if shipment:
                    shipment["created_at"] = format_datetime(pd.to_datetime(shipment["created_at"]))
                    shipment_display = {
                        "Трек-код": shipment["track_code"],
                        "Код клиента": shipment["client_code"],
                        "Описание": shipment["description"],
                        "Дата добавления": shipment["created_at"],
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
                        conn.execute(
                            """
                            UPDATE shipments
                            SET arrived = :arrived, issued = :issued
                            WHERE track_code = :track_code
                            """,
                            {"arrived": arrived, "issued": issued, "track_code": track_code}
                        )
                        st.success("Статус груза обновлен!")
                else:
                    st.warning("Данные по этому трек-коду не найдены.")
        else:
            st.error("QR или штрих-код не распознан.")

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
                    track_code = obj.data.decode("utf-8").replace(" ", "")
                    st.write(f"Распознанный трек-код: {track_code}")

                    # Поиск в базе данных
                    result = conn.query("SELECT * FROM shipments WHERE track_code = :track_code", {"track_code": track_code})
                    shipment = result[0] if result else None

                    if shipment:
                        shipment["created_at"] = format_datetime(pd.to_datetime(shipment["created_at"]))
                        shipment_display = {
                            "Трек-код": shipment["track_code"],
                            "Код клиента": shipment["client_code"],
                            "Описание": shipment["description"],
                            "Дата добавления": shipment["created_at"],
                            "Прибыл": "Да" if shipment["arrived"] else "Нет",
                            "Выдан": "Да" if shipment["issued"] else "Нет"
                        }
                        st.write("Информация о грузе:", shipment_display)

                        # Обновление состояния груза
                        with st.form(f"update_status_{track_code}"):
                            arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                            issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                            update_submitted = st.form_submit_button("Обновить статус")

                        if update_submitted:
                            conn.execute(
                                """
                                UPDATE shipments
                                SET arrived = :arrived, issued = :issued
                                WHERE track_code = :track_code
                                """,
                                {"arrived": arrived, "issued": issued, "track_code": track_code}
                            )
                            st.success("Статус груза обновлен!")
                    else:
                        st.warning("Данные по этому трек-коду не найдены.")
            else:
                st.error("QR или штрих-код не распознан.")
