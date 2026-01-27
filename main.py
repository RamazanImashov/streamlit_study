import streamlit as st

pages = {
    "Страницы": [
        st.Page("pages/horizon_pull_users.py", title="Клиенты Horizon"),
        st.Page("pages/stats.py", title="Статистика"),
        st.Page("pages/download_users_file.py", title="Загрузка данных клиентов"),
        st.Page("pages/dcodegenerator.py", title="Создание D код изображений"),
    ],
}

pg = st.navigation(pages)
pg.run()
