from __future__ import annotations

from pathlib import Path
import re

import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from utils.api_client import get_clients


CANVAS_W = 1080
CANVAS_H = 2133

TEMPLATE_DIR = Path("templates")

CODE_RE = re.compile(r"^(?:DK|D)?(?P<num>\d+)$", re.IGNORECASE)


@st.cache_data(ttl=60)
def load_clients():
    return get_clients()


def extract_code_number(raw_code: str) -> str:
    """
    DK58 -> 58
    D58  -> 58
    58   -> 58
    """
    if raw_code is None:
        return ""

    code = str(raw_code).strip().upper()

    match = CODE_RE.match(code)
    if not match:
        return code

    return match.group("num")


def make_display_code(raw_code: str) -> str:
    """
    DK58 -> DK58
    D58  -> DK58
    58   -> DK58
    """
    number = extract_code_number(raw_code)

    if not number:
        return ""

    if number.isdigit():
        return f"DK{number}"

    return number


def sort_code(raw_code: str):
    number = extract_code_number(raw_code)

    if number.isdigit():
        return int(number)

    return 10**9


def render_html(code_number: str) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    tpl = env.get_template("dk-code-template-editable.html")

    # ВАЖНО:
    # если в HTML уже написано DK{{ code }},
    # сюда передаем только номер: 58
    return tpl.render(code=code_number)


def html_to_png_bytes(html: str) -> bytes:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage"],
        )

        context = browser.new_context(
            viewport={"width": CANVAS_W, "height": CANVAS_H},
            device_scale_factor=1,
            locale="ru-RU",
        )

        page = context.new_page()
        page.set_content(html, wait_until="load")

        png = page.screenshot(type="png", full_page=False)

        context.close()
        browser.close()

        return png


def client_label(client: dict) -> str:
    display_code = make_display_code(client.get("code_client", ""))

    name = (
        client.get("name")
        or client.get("full_name")
        or client.get("title")
        or client.get("company_name")
        or ""
    )

    if name:
        return f"{display_code} — {name}"

    return display_code


st.set_page_config(page_title="Horizon PNG Generator", layout="centered")
st.title("Horizon: генератор PNG по коду")


try:
    clients = load_clients()
except Exception as e:
    st.error(f"Не удалось получить клиентов: {e}")
    st.stop()


if not clients:
    st.warning("Список клиентов пуст.")
    st.stop()


clients_with_codes = []

for client in clients:
    code_number = extract_code_number(client.get("code_client", ""))

    if not code_number:
        continue

    client_copy = dict(client)
    client_copy["code_number"] = code_number
    client_copy["display_code"] = make_display_code(client.get("code_client", ""))

    clients_with_codes.append(client_copy)


if not clients_with_codes:
    st.warning("Нет клиентов с кодами.")
    st.stop()


clients_sorted = sorted(
    clients_with_codes,
    key=lambda c: sort_code(c["code_number"]),
)


selected_client = st.selectbox(
    "Выберите клиента",
    options=clients_sorted,
    format_func=client_label,
)


code_number = selected_client["code_number"]      # 58
display_code = selected_client["display_code"]    # DK58

st.write(f"Выбранный код: **{display_code}**")


if st.button("Сгенерировать PNG", type="primary"):
    html = render_html(code_number)
    png_bytes = html_to_png_bytes(html)

    st.image(png_bytes, caption=display_code, use_container_width=True)

    st.download_button(
        "Скачать PNG",
        data=png_bytes,
        file_name=f"HORIZON_{display_code}.png",
        mime="image/png",
    )