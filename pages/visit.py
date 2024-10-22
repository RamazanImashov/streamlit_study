import streamlit as st
from jinja2 import Template
import imgkit
from io import BytesIO
import os
from utils import get_clients, get_contacts, get_warehouse_data, get_social_media


def create_png_from_html(client_data, warehouse_data, contacts, social_media):
    with open("templates/code_card.html", "r", encoding="utf-8") as file:
        template = Template(file.read())

    html_content = template.render(
        client_code=client_data['code_client'],
        client_name=client_data['username'],
        client_phone=client_data['phone_number'],
        warehouse_data=warehouse_data,
        company_email=contacts[0]['contact'],
        company_address=contacts[1]['contact'],
        company_phone=contacts[2]['contact'],
        social_media=social_media,
        logo_path="/absolute/path/to/logo.png",
        css_path="/absolute/path/to/style/code_card.css"
    )

    temp_html_path = "/tmp/output.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    path_to_wkhtmltoimage = '/usr/local/bin/wkhtmltoimage'
    config = imgkit.config(wkhtmltoimage=path_to_wkhtmltoimage)

    tmp_file_path = "/tmp/output.png"

    imgkit.from_file(
        temp_html_path,
        tmp_file_path,
        config=config,
        options={
            "format": "png",
            "--enable-local-file-access": "",
            "encoding": "UTF-8"
        }
    )

    with open(tmp_file_path, "rb") as f:
        img_buffer = BytesIO(f.read())

    os.remove(temp_html_path)
    os.remove(tmp_file_path)

    img_buffer.seek(0)
    return img_buffer


st.title("Генерация визитки клиента")

clients = get_clients()
client_options = {client["code_client"]: client for client in sorted(clients, key=lambda x: x["code_client"])}
selected_client_code = st.selectbox("Выберите клиента", options=client_options.keys())
selected_client = client_options[selected_client_code]

contacts = get_contacts()
social_media = get_social_media()

if st.button("Создать визитку"):
    warehouse_data = get_warehouse_data()
    if selected_client and warehouse_data and contacts and social_media:
        image_buffer = create_png_from_html(selected_client, warehouse_data, contacts, social_media)
        if image_buffer:
            st.image(image_buffer, caption="Визитка клиента", use_column_width=True)
            st.download_button("Скачать визитку", data=image_buffer,
                               file_name=f"{selected_client['code_client']}_card.png", mime="image/png")
