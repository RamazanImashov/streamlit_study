from __future__ import annotations

from pathlib import Path
import re

import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from utils.api_client import get_clients_dordoi


CANVAS_W = 1080
CANVAS_H = 1901
TEMPLATE_DIR = Path("templates")

CODE_RE = re.compile(r"^(?P<prefix>[A-Za-z]+)(?P<num>\d+)$")


def sort_code(code: str):
    if not code:
        return ("", 10**9)
    m = CODE_RE.match(code)
    if not m:
        return (code, 10**9)
    return (m.group("prefix"), int(m.group("num")))


@st.cache_data(ttl=60)
def load_clients():
    return get_clients_dordoi()


def render_html(code: str) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    tpl = env.get_template("f-code-template-editable.html")
    return tpl.render(code=code)


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

clients_sorted = sorted(clients, key=lambda c: sort_code(c.get("code_client", "")))

def label(c: dict) -> str:
    code = c.get("code_client", "")
    name = c.get("name") or c.get("full_name") or c.get("title") or ""
    return f"{code} — {name}" if name else code

selected_client = st.selectbox(
    "Выберите клиента",
    options=clients_sorted,
    format_func=label,
)

code = selected_client.get("code_client", "")
if not code:
    st.error("У выбранного клиента нет code_client.")
    st.stop()

st.write(f"Выбранный код: {code}")

if st.button("Сгенерировать PNG", type="primary"):
    html = render_html(code)
    png_bytes = html_to_png_bytes(html)

    st.image(png_bytes, caption=code, use_column_width=True)
    st.download_button(
        "Скачать PNG",
        data=png_bytes,
        file_name=f"HORIZON_{code}.png",
        mime="image/png",
    )
