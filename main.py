import streamlit as st

pages = {
    "Pages": [
        st.Page("pages/pull_users.py", title="Пользователи"),
        st.Page("pages/send_message.py", title="Отправить сообщение"),
        st.Page("pages/visit.py", title="Визитка"),
        st.Page("pages/barcode_scanner.py", title="Сканер штрих кода"),
    ],
}

pg = st.navigation(pages)
pg.run()
