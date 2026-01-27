import streamlit as st

pages = {
    "Страницы": [
        st.Page("pages/dordoi_pull_users.py", title="Пользователи Дордой"),
        st.Page("pages/download_users_file.py", title="Загрузка данных"),
        st.Page("pages/fcodegenerator.py", title="Создание F код изображений"),
    ],
}

pg = st.navigation(pages)
pg.run()
