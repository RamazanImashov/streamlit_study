import streamlit as st
import requests
from utils.get_client import get_clients


# 2. Загрузка данных клиентов
clients = get_clients()

# Сортируем клиентов по возрастанию имени
clients_sorted = sorted(clients, key=lambda client: client["code_client"])

# Преобразуем клиентов в словарь для удобного выбора
client_options = {client["code_client"]: client for client in clients_sorted}

# 3. Интерфейс
st.title("Отправка информации клиентам")

# Выбор одного или нескольких клиентов
selected_clients_names = st.multiselect("Выберите одного или нескольких клиентов", options=list(client_options.keys()))

# Если выбран хотя бы один клиент
if selected_clients_names:
    # Получаем данные выбранных клиентов
    selected_clients = [client_options[client_name] for client_name in selected_clients_names]

    # Если выбран только один клиент
    if len(selected_clients) == 1:
        selected_client = selected_clients[0]

        # Отображение информации о клиенте
        st.subheader(f"Данные клиента: {selected_client['username']}")

        # Проверяем наличие каждого поля и выводим данные
        st.write(f"**Имя:** {selected_client['username']}")
        st.write(f"**Email:** {selected_client['email'] if selected_client['email'] else 'Не указан'}")
        st.write(f"**Номер телефона:** {selected_client['phone_number'] if selected_client['phone_number'] else 'Не указан'}")
        st.write(f"**Код клиента:** {selected_client['code_client']}")

        # Поле для ввода веса и цены только при выборе одного клиента
        weight = st.number_input("Введите вес (кг)", min_value=0.0, format="%.2f")
        price = st.number_input("Введите цену (в доллар США)", min_value=0.0, format="%.2f")

        # Текст сообщения (по умолчанию) с возможностью редактирования
        default_message = f"Здравствуйте, {selected_client['username']}! Ваш груз весит {weight} кг и стоит {price} $."
        custom_message = st.text_area("Сообщение для отправки", value=default_message)

        # Кнопка для отправки сообщения
        if st.button("Отправить сообщение"):
            if not selected_client['phone_number']:
                st.error("У выбранного клиента нет номера телефона.")
            else:
                # Формирование WhatsApp ссылки
                whatsapp_url = f"https://api.whatsapp.com/send?phone={selected_client['phone_number']}&text={custom_message}"
                js = f"window.open('{whatsapp_url}');"
                st.components.v1.html(f"<script>{js}</script>", height=0)

    # Если выбрано несколько клиентов
    else:
        st.subheader("Сообщения будут отправлены следующим клиентам:")

        # Отображаем информацию о каждом выбранном клиенте
        for client in selected_clients:
            st.write(f"**Имя:** {client['username']}")
            st.write(f"**Email:** {client['email'] if client['email'] else 'Не указан'}")
            st.write(f"**Номер телефона:** {client['phone_number'] if client['phone_number'] else 'Не указан'}")
            st.write(f"**Код клиента:** {client['code_client']}")
            st.write("---")

        # Текст сообщения (по умолчанию) для всех клиентов с возможностью редактирования
        default_message = "Здравствуйте! Мы уведомляем вас о вашем заказе. Если у вас есть вопросы, свяжитесь с нами."
        custom_message = st.text_area("Сообщение для отправки всем клиентам", value=default_message)

        # Кнопка для отправки сообщения всем клиентам
        if st.button("Отправить сообщения всем клиентам"):
            for client in selected_clients:
                if not client['phone_number']:
                    st.error(f"У клиента {client['username']} нет номера телефона.")
                else:
                    # Формирование WhatsApp ссылки
                    whatsapp_url = f"https://api.whatsapp.com/send?phone={client['phone_number']}&text={custom_message}"
                    js = f"window.open('{whatsapp_url}');"
                    st.components.v1.html(f"<script>{js}</script>", height=0)



if __name__ == "__main__":
    # Запуск приложения только если оно запускается через Streamlit
    st.title("Отправка информации клиентам")