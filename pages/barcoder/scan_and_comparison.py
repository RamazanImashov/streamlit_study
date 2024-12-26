

def scan_by_image():
    import streamlit as st
    import pandas as pd
    from pyzbar.pyzbar import decode
    from PIL import Image
    from utils.utils import format_datetime
    from utils.api_client import (get_from_api_orders,
                                  patch_to_api_order)

    st.title("Сканирование и сравнение")

    # Сканирование через загрузку изображения
    st.header("Сканирование через загрузку изображения")
    uploaded_file = st.file_uploader("Загрузите изображение с QR или штрих-кодом", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Загруженное изображение")

        # Декодирование QR или штрих-кода
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                track_code = obj.data.decode("utf-8").replace(" ", "")
                st.write(f"Распознанный трек-код: {track_code}")

                # Поиск в базе данных через API
                shipment = get_from_api_orders(f"?search={track_code}")

                if shipment:
                    shipment_display = {
                        "Трек-код": shipment["track_code"],
                        "Клиент": shipment["client_name"],
                        "Описание": shipment["description"],
                        "Дата добавления": format_datetime(pd.to_datetime(shipment["created_at"])),
                        "Прибыл": "Да" if shipment["arrived"] else "Нет",
                        "Выдан": "Да" if shipment["issued"] else "Нет"
                    }
                    st.write("Информация о грузе:", shipment_display)

                    # Обновление состояния груза
                    with st.form(f"update_status_{track_code}_file"):
                        arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                        issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                        update_submitted = st.form_submit_button("Обновить статус")

                    if update_submitted:
                        order_id_form_track_code = get_from_api_orders(f"?search={track_code}")
                        patch_to_api_order(order_id_form_track_code[0][1], {
                            "arrived": arrived,
                            "issued": issued
                        })
                        st.success("Статус груза обновлен!")
                else:
                    st.warning("Данные по этому трек-коду не найдены.")
        else:
            st.error("QR или штрих-код не распознан.")


def scan_by_camera():
    import streamlit as st
    from pyzbar.pyzbar import decode
    from PIL import Image
    from io import BytesIO
    import pandas as pd
    from utils.utils import format_datetime
    import requests
    from datetime import datetime
    from utils.api_client import get_from_api_orders, post_to_api_order, delete_to_api_order, patch_to_api_order

    st.title("Сканирование и сравнение")

    # Инструкция для пользователя
    st.info(
        "Для использования камеры:\n"
        "1. Убедитесь, что вы предоставили разрешение на использование камеры в вашем браузере.\n"
        "2. Если браузер запросил доступ, подтвердите его.\n"
        "3. Убедитесь, что устройство оснащено рабочей камерой."
    )

    # Сканирование через камеру
    st.header("Сканирование через камеру")
    enable = st.checkbox("Включить камеру")

    if not enable:
        st.warning("Камера отключена. Включите камеру для сканирования.")
    else:
        picture = st.camera_input("Take a picture", disabled=not enable)

        if picture:
            st.image(picture, caption="Ваш снимок")

            # Декодирование QR или штрих-кода
            image = Image.open(BytesIO(picture.getvalue()))
            decoded_objects = decode(image)

            if decoded_objects:
                for obj in decoded_objects:
                    track_code = obj.data.decode("utf-8")

                    st.write(f"Распознанный трек-код: {track_code}")

                    # Поиск в базе данных
                    shipment = get_from_api_orders(f"?search={track_code}")
                    if shipment:
                        shipment_display = {
                            "Трек-код": shipment["track_code"],
                            "Клиент": shipment["client_name"],
                            "Описание": shipment["description"],
                            "Дата добавления": format_datetime(pd.to_datetime(shipment["created_at"])),
                            "Прибыл": "Да" if shipment["arrived"] else "Нет",
                            "Выдан": "Да" if shipment["issued"] else "Нет"
                        }
                        st.write("Информация о грузе:", shipment_display)

                        # Обновление состояния груза
                        with st.form(f"update_status_{track_code}_file"):
                            arrived = st.checkbox("Груз прибыл", value=shipment.get("arrived", False))
                            issued = st.checkbox("Груз выдан", value=shipment.get("issued", False))
                            update_submitted = st.form_submit_button("Обновить статус")

                        if update_submitted:
                            order_id_form_track_code = get_from_api_orders(f"?search={track_code}")
                            patch_to_api_order(order_id_form_track_code[0][1], {
                                "arrived": arrived,
                                "issued": issued
                            })
                            st.success("Статус груза обновлен!")
                    else:
                        st.warning("Данные по этому трек-коду не найдены.")
            else:
                st.error("QR или штрих-код не распознан.")
