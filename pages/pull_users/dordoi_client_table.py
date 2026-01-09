
def dordoi_clients():
    import streamlit as st
    import pandas as pd
    import io
    from utils.api_client import get_clients_dordoi
    from utils.to_excel import to_excel

    st.title("Список клиентов и экспорт данных")

    clients = get_clients_dordoi()

    if clients:
        df = pd.DataFrame(clients)

        columns_to_show = {
            "username": "Имя",
            "phone_number": "Номер телефона",
            "code_client": "Код клиента",
            "manager": "Менеджер"
        }

        df_display = df[list(columns_to_show.keys())].rename(columns=columns_to_show)

        df_display = df_display.sort_values("Код клиента")

        st.subheader("Все клиенты")
        st.dataframe(df_display, use_container_width=True)

        excel_data = to_excel(df_display)

        st.download_button(
            label="📥 Скачать таблицу в Excel",
            data=excel_data,
            file_name="clients_dordoi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Данные о клиентах не найдены.")
