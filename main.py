import streamlit as st

pages = {
    "Pages": [
        st.Page("pages/pull_users.py", title="Пользователи hor-log"),
        st.Page("pages/dordoi_pull_users.py", title="Пользователи Дордой"),
        st.Page("pages/send_message.py", title="Отправить сообщение"),
        st.Page("pages/stats.py", title="Статистика"),
        st.Page("pages/barcode_scanner.py", title="Сканер штрих кода"),
    ],
}

pg = st.navigation(pages)
pg.run()
