def horizon_clients():
    import streamlit as st
    import pandas as pd
    import io
    from utils.api_client import get_clients
    from utils.to_excel import to_excel

    st.title("Список всех клиентов")
    clients = get_clients()
    if clients:
        df = pd.DataFrame(clients)
        columns_mapping = {
            "username": "Имя",
            "phone_number": "Номер телефона",
            "code_client": "Код клиента"
        }
        df_display = df[list(columns_mapping.keys())].rename(columns=columns_mapping)
        df_display = df_display.sort_values("Код клиента")
        st.subheader("Таблица пользователей")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        excel_file = to_excel(df_display)

        st.download_button(
            label="📂 Скачать список в Excel",
            data=excel_file,
            file_name="all_clients.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Не удалось загрузить данные о клиентах.")
