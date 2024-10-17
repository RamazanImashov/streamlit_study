import streamlit as st

pages = {
    "Users": [
        st.Page("pages/pull_users.py", title="Пользователи"),
    ],
    "Pages": [
        st.Page("pages/send_message.py", title="Отправить сообщение"),
        st.Page("pages/visit.py", title="Визитка"),
    ],
}

pg = st.navigation(pages)
pg.run()