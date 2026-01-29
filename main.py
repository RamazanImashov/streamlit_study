import streamlit as st

pages = {
    "Страницы": [
        st.Page("pages/dordoi_pull_users.py", title="Клиенты Дордой"),
        st.Page("pages/download_users_file.py", title="Загрузка данных"),
        st.Page("pages/fcodegenerator.py", title="Создание F код изображений"),
        st.Page("pages/01_free_f_codes.py", title="Свободные F коды"),
    ],
}

pg = st.navigation(pages)
pg.run()
