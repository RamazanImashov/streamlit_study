import streamlit as st
import sqlite3
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
from decouple import config

Conn_name = config("CONNAME")

# Подключение к SQLite
conn = sqlite3.connect(Conn_name)
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_code TEXT NOT NULL,
    client_code TEXT NOT NULL,
    description TEXT
)
''')
conn.commit()


# Выбор страницы
page = st.sidebar.selectbox("Навигация", ["Обзор базы", "Добавить данные", "Сканирование и сравнение"])

if page == "Обзор базы":
    st.title("Обзор базы данных")

    # Загрузка данных из SQLite
    cursor.execute("SELECT * FROM shipments")
    data = cursor.fetchall()
    columns = ["ID", "Track Code", "Client Code", "Description"]
    df = pd.DataFrame(data, columns=columns)

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
        # Сохранение данных в SQLite
        if track_code and client_code:
            cursor.execute(
                "INSERT INTO shipments (track_code, client_code, description) VALUES (?, ?, ?)",
                (track_code, client_code, description),
            )
            conn.commit()
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
        picture = st.camera_input("Сделать снимок")

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
                    cursor.execute("SELECT * FROM shipments WHERE track_code = ?", (track_code,))
                    shipment = cursor.fetchone()
                    if shipment:
                        st.write("Информация о грузе:", {
                            "ID": shipment[0],
                            "Track Code": shipment[1],
                            "Client Code": shipment[2],
                            "Description": shipment[3],
                        })
                    else:
                        st.warning("Данные по этому трек-коду не найдены.")
            else:
                st.error("QR или штрих-код не распознан.")
