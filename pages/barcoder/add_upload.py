

def upload_excel_order():
    import streamlit as st
    import pandas as pd
    from utils.api_client import post_to_api_order

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
                # Очистка данных от недопустимых значений
                df = df.fillna("")  # Заменить NaN на пустую строку

                # Добавление данных через API
                for _, row in df.iterrows():
                    data = {
                        "track_code": row["Трек-код"],
                        "client_code": row["Код клиента"],
                        "description": row.get("Описание", "")
                    }

                    # Проверка значений перед отправкой
                    if not data["track_code"] or not data["client_code"]:
                        st.error("Пустые значения обнаружены в строке. Пропуск.")
                        continue

                    response = post_to_api_order(data)
                    if response is None:
                        st.error(f"Ошибка при обработке строки с трек-кодом: {data['track_code']}")

                st.success("Данные из Excel успешно загружены в базу!")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")

    st.title("Добавить данные в базу")



def add_order():
    import streamlit as st
    from utils.api_client import post_to_api_order

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
