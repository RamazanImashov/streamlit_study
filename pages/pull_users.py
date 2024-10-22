from utils.get_client import get_clients
import streamlit as st


clients = get_clients()

clients_sorted = sorted(clients, key=lambda client: client["code_client"])

client_options = {client["code_client"]: client for client in clients_sorted}

st.title("Отправка информации клиентам")

selected_client_name = st.selectbox("Выберите клиента", options=list(client_options.keys()))


selected_client = client_options[selected_client_name]

st.subheader(f"Данные клиента: {selected_client_name}")

st.write(f"**Имя:** {selected_client['username']}")
st.write(f"**Email:** {selected_client['email'] if selected_client['email'] else 'Не указан'}")
st.write(f"**Номер телефона:** {selected_client['phone_number'] if selected_client['phone_number'] else 'Не указан'}")
st.write(f"**Код клиента:** {selected_client['code_client']}")
