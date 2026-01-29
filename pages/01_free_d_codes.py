# pages/01_d_codes.py
from __future__ import annotations

import re
import urllib.parse
from typing import Any

import pandas as pd
import streamlit as st

from utils.api_client import get_clients

from config import CONFIG_ADMIN_ADD_URL, CONFIG_RETURN_URL

CODE_RE = re.compile(r"^(?P<prefix>[A-Za-z]+)(?P<num>\d+)$")

ADMIN_ADD_URL = CONFIG_ADMIN_ADD_URL
ADMIN_TAB_FRAGMENT = "#персональная-информация-tab"
RETURN_URL = CONFIG_RETURN_URL


def make_code(n: int) -> str:
    return f"D{n:02d}" if 1 <= n <= 99 else f"D{n}"


def parse_num(code: str) -> int | None:
    m = CODE_RE.match((code or "").strip().upper())
    if not m:
        return None
    try:
        return int(m.group("num"))
    except ValueError:
        return None


def norm_phone(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip())


def extract_manager_choices(clients: list[dict[str, Any]]) -> tuple[list[str], dict[str, str]]:
    seen = {}
    for c in clients:
        m = c.get("manager")
        if m is None or m == "":
            continue

        mid = None
        mname = None

        if isinstance(m, dict):
            mid = m.get("id") or m.get("pk") or m.get("value")
            mname = m.get("name") or m.get("title") or m.get("label")
        elif isinstance(m, int):
            mid = m
        elif isinstance(m, str):
            mname = m.strip()

        if mid is not None and str(mid).strip():
            label = f"ID {mid}" if not mname else f"{mname} (ID {mid})"
            seen[label] = str(mid)
        elif mname:
            seen[mname] = mname

    labels = sorted(seen.keys(), key=lambda x: x.lower())
    return labels, seen


@st.cache_data(ttl=60)
def load_clients_cached():
    return get_clients() or []


@st.cache_data(ttl=60)
def load_used_nums() -> set[int]:
    clients = load_clients_cached()
    used = set()
    for c in clients:
        code = (c.get("code_client") or "").strip().upper()
        if not code.startswith("D"):
            continue
        n = parse_num(code)
        if n is None:
            continue
        if 1 <= n <= 500:
            used.add(n)
    return used


st.set_page_config(page_title="Коды D01…D500", layout="wide")
st.title("Коды клиентов D01…D500")

clients = load_clients_cached()
used_nums = load_used_nums()

with st.expander("Фильтры", expanded=False):
    only_free = st.checkbox("Показывать только свободные", value=False)
    search = st.text_input("Поиск (D07 / D100 / 7 / 100)", "").strip().upper()

rows_meta = []
display_rows = []
for n in range(1, 501):
    is_used = n in used_nums
    code = make_code(n)

    if only_free and is_used:
        continue

    if search:
        q = search
        if q.isdigit():
            qn = int(q)
            q = make_code(qn) if 1 <= qn <= 500 else q
        if q not in code:
            continue

    dot = "🔴" if is_used else "🟢"
    status = "занято" if is_used else "свободно"

    rows_meta.append({"num": n, "code": code, "used": is_used})
    display_rows.append({"": dot, "Код": code, "Статус": status})

df = pd.DataFrame(display_rows)

st.caption(f"Занято: {len(used_nums)} • Свободно: {500 - len(used_nums)}")

col1, col2 = st.columns([2, 1], vertical_alignment="top")

with col1:
    selected_code = None
    selected_used = None

    try:
        ev = st.dataframe(
            df,
            use_container_width=True,
            height=680,
            hide_index=True,
            column_config={
                "": st.column_config.TextColumn("", width="small"),
                "Код": st.column_config.TextColumn("Код", width="small"),
                "Статус": st.column_config.TextColumn("Статус", width="small"),
            },
            on_select="rerun",
            selection_mode="single-row",
        )

        if getattr(ev, "selection", None) and ev.selection.rows:
            idx = ev.selection.rows[0]
            st.session_state["dcode_selected_idx"] = idx

        idx = st.session_state.get("dcode_selected_idx")
        if idx is not None and 0 <= idx < len(rows_meta):
            selected_code = rows_meta[idx]["code"]
            selected_used = rows_meta[idx]["used"]

    except TypeError:
        st.dataframe(df, use_container_width=True, height=680, hide_index=True)
        selected_code = st.selectbox("Выберите код", options=[r["code"] for r in rows_meta], index=None)
        if selected_code:
            n = parse_num(selected_code) or -1
            selected_used = (n in used_nums)

with col2:
    st.subheader("Создание клиента")

    if not selected_code:
        st.info("Выберите код слева.")
        st.stop()

    if selected_used:
        st.error(f"{selected_code} занято. Выберите зелёный код.")
        st.stop()

    st.success(f"Выбран свободный код: {selected_code}")

    first_name = st.text_input("Имя", placeholder="Например: Айбек")
    last_name = st.text_input("Фамилия", placeholder="Например: Токтогулов")
    phone_number = st.text_input("Номер телефона", placeholder="+996...", value="")
    phone_number = norm_phone(phone_number)

    labels, mapping = extract_manager_choices(clients)
    manager_value: str | None = None
    if labels:
        chosen_label = st.selectbox("Менеджер", options=["—"] + labels, index=0)
        if chosen_label != "—":
            manager_value = mapping[chosen_label]
    else:
        manager_value = st.text_input("Менеджер (имя или ID)", placeholder="Например: Нурбек или 3").strip() or None

    comment = st.text_area("Комментарий", placeholder="Любые заметки по клиенту", height=110)

    username = ""
    if (first_name or last_name):
        username = f"{last_name} {first_name}".strip()

    confirm = st.checkbox("Подтверждаю выбор кода и данных", value=False)

    if confirm:
        params = {
            "code_client": selected_code,
            "next": RETURN_URL,
        }

        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name
        if phone_number:
            params["phone_number"] = phone_number
        if username:
            params["username"] = username
        if manager_value:
            params["manager"] = manager_value
        if comment:
            params["client_ditail"] = comment

        admin_url = ADMIN_ADD_URL + "?" + urllib.parse.urlencode(params) + ADMIN_TAB_FRAGMENT
        st.link_button("Перейти в админку и создать клиента", admin_url, use_container_width=True)
    else:
        st.warning("Поставьте подтверждение, чтобы активировать переход.")
