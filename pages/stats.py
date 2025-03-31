import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from config import (
    DEFAULT_API,
    DORDOI_CLIENT_API_URL, 
    MANAGER_API_URL
)

# URL для получения статистики через API
API_URL = DEFAULT_API

# Функция для загрузки данных с API
def get_stats():
    response = requests.get(API_URL+MANAGER_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка загрузки данных")
        return {}

# Загрузка статистики
data = get_stats()

# Преобразуем данные в DataFrame
df = pd.DataFrame(list(data.items()), columns=["Manager", "Clients"])

# Отображаем таблицу
st.title('Статистика по менеджерам')
st.write(df)

# Построение столбчатой диаграммы
fig, ax = plt.subplots()
ax.bar(df['Manager'], df['Clients'], color='skyblue')
ax.set_xlabel('Менеджеры')
ax.set_ylabel('Количество клиентов')
ax.set_title('Количество клиентов по менеджерам')
plt.xticks(rotation=45, ha="right")

st.pyplot(fig)
