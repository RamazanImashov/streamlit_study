

def get_order():
    import streamlit as st
    import pandas as pd
    from io import BytesIO
    from datetime import datetime
    from utils.api_client import get_from_api_orders
    from utils.utils import format_datetime

    st.title("Обзор базы данных")

    # Загрузка данных из API
    data = get_from_api_orders()
    df = pd.DataFrame(data)

    # Преобразование формата даты
    if "created_at" in df.columns:
        try:
            df["created_at"] = pd.to_datetime(df["created_at"], format="mixed", errors="coerce")
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
        except Exception as e:
            st.error(f"Ошибка при обработке дат: {e}")
    else:
        st.dataframe(df)


def delete_order():
    import streamlit as st
    from utils.api_client import get_from_api_orders, delete_to_api_order

    st.title("Удаление записей из базы данных")

    # Удаление записи
    track_code_to_delete = st.text_input("Введите трек-код для удаления")
    if st.button("Удалить запись"):
        try:
            # Получение данных заказа
            orders = get_from_api_orders()
            order = next((o for o in orders if o["track_code"] == track_code_to_delete), None)

            if not order:
                st.error("Запись с таким трек-кодом не найдена!")
                return

            # Удаление через API
            result = delete_to_api_order(order["id"])  # Передаем только ID

            if result and "message" in result:
                st.success(result["message"])
            else:
                st.success(f"Запись с трек-кодом {track_code_to_delete} успешно удалена!")
        except Exception as e:
            st.error(f"Ошибка при удалении записи: {e}")



