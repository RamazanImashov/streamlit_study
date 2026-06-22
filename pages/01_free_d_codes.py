# pages/01_dk_codes.py
from __future__ import annotations

import re
import urllib.parse
from typing import Any

import pandas as pd
import streamlit as st

from utils.api_client import get_clients
from config import CONFIG_ADMIN_ADD_URL, CONFIG_RETURN_URL


CODE_RE = re.compile(r"^(?P<prefix>DK|D)?(?P<num>\d+)$", re.IGNORECASE)

ADMIN_ADD_URL = CONFIG_ADMIN_ADD_URL
ADMIN_TAB_FRAGMENT = "#персональная-информация-tab"
RETURN_URL = CONFIG_RETURN_URL

MAX_CODE = 500


def make_code(n: int) -> str:
    """
    1   -> DK01
    9   -> DK09
    10  -> DK10
    500 -> DK500
    """
    return f"DK{n:02d}" if 1 <= n <= 99 else f"DK{n}"


def parse_num(code: str | None) -> int | None:
    """
    DK58 -> 58
    D58  -> 58
    58   -> 58
    """
    raw = (code or "").strip().upper()
    if not raw:
        return None

    match = CODE_RE.match(raw)
    if not match:
        return None

    try:
        return int(match.group("num"))
    except ValueError:
        return None


def normalize_code(code: str | None) -> str:
    """
    DK58 -> DK58
    D58  -> DK58
    58   -> DK58
    """
    n = parse_num(code)
    if n is None:
        return ""
    return make_code(n)


def norm_phone(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip())


def extract_manager_choices(
    clients: list[dict[str, Any]],
) -> tuple[list[str], dict[str, str]]:
    seen: dict[str, str] = {}

    for client in clients:
        manager = client.get("manager")

        if manager is None or manager == "":
            continue

        manager_id = None
        manager_name = None

        if isinstance(manager, dict):
            manager_id = (
                manager.get("id")
                or manager.get("pk")
                or manager.get("value")
            )
            manager_name = (
                manager.get("name")
                or manager.get("title")
                or manager.get("label")
            )

        elif isinstance(manager, int):
            manager_id = manager

        elif isinstance(manager, str):
            manager_name = manager.strip()

        if manager_id is not None and str(manager_id).strip():
            label = (
                f"ID {manager_id}"
                if not manager_name
                else f"{manager_name} (ID {manager_id})"
            )
            seen[label] = str(manager_id)

        elif manager_name:
            seen[manager_name] = manager_name

    labels = sorted(seen.keys(), key=lambda x: x.lower())
    return labels, seen


@st.cache_data(ttl=60)
def load_clients_cached() -> list[dict[str, Any]]:
    return get_clients() or []


@st.cache_data(ttl=60)
def load_used_nums() -> set[int]:
    """
    ВАЖНО:
    Если в базе ещё остались старые D58, мы тоже считаем их занятыми.
    Иначе можно случайно создать DK58 поверх старого D58.
    """
    clients = load_clients_cached()
    used: set[int] = set()

    for client in clients:
        raw_code = (client.get("code_client") or "").strip().upper()
        n = parse_num(raw_code)

        if n is None:
            continue

        if 1 <= n <= MAX_CODE:
            used.add(n)

    return used


def build_admin_url(params: dict[str, str]) -> str:
    return (
        ADMIN_ADD_URL
        + "?"
        + urllib.parse.urlencode(params)
        + ADMIN_TAB_FRAGMENT
    )


st.set_page_config(page_title="Коды DK01…DK500", layout="wide")
st.title("Коды клиентов DK01…DK500")

if st.button("Обновить список клиентов"):
    load_clients_cached.clear()
    load_used_nums.clear()
    st.rerun()

clients = load_clients_cached()
used_nums = load_used_nums()

with st.expander("Фильтры", expanded=False):
    only_free = st.checkbox("Показывать только свободные", value=False)
    search = st.text_input(
        "Поиск (DK07 / D07 / 7 / 100)",
        "",
    ).strip().upper()


rows_meta: list[dict[str, Any]] = []
display_rows: list[dict[str, str]] = []

for n in range(1, MAX_CODE + 1):
    is_used = n in used_nums
    code = make_code(n)

    if only_free and is_used:
        continue

    if search:
        search_num = parse_num(search)

        if search_num is not None:
            search_code = make_code(search_num)
            if search_code not in code:
                continue
        else:
            if search not in code:
                continue

    dot = "🔴" if is_used else "🟢"
    status = "занято" if is_used else "свободно"

    rows_meta.append(
        {
            "num": n,
            "code": code,
            "used": is_used,
        }
    )

    display_rows.append(
        {
            "": dot,
            "Код": code,
            "Статус": status,
        }
    )


df = pd.DataFrame(display_rows)

st.caption(f"Занято: {len(used_nums)} • Свободно: {MAX_CODE - len(used_nums)}")

col1, col2 = st.columns([2, 1], vertical_alignment="top")

with col1:
    selected_code: str | None = None
    selected_used: bool | None = None

    if df.empty:
        st.warning("По фильтрам ничего не найдено.")
    else:
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

                if 0 <= idx < len(rows_meta):
                    st.session_state["dkcode_selected_code"] = rows_meta[idx]["code"]

            selected_code = st.session_state.get("dkcode_selected_code")

            if selected_code:
                selected_num = parse_num(selected_code)
                selected_used = selected_num in used_nums if selected_num else None

        except TypeError:
            st.dataframe(
                df,
                use_container_width=True,
                height=680,
                hide_index=True,
            )

            selected_code = st.selectbox(
                "Выберите код",
                options=[row["code"] for row in rows_meta],
                index=None,
            )

            if selected_code:
                selected_num = parse_num(selected_code)
                selected_used = selected_num in used_nums if selected_num else None


with col2:
    st.subheader("Создание клиента")

    if not selected_code:
        st.info("Выберите код слева.")
        st.stop()

    selected_code = normalize_code(selected_code)

    if selected_used:
        st.error(f"{selected_code} занято. Выберите зелёный код.")
        st.stop()

    st.success(f"Выбран свободный код: {selected_code}")

    first_name = st.text_input("Имя", placeholder="Например: Айбек")
    last_name = st.text_input("Фамилия (ОсОО)", placeholder="Например: Токтогулов")

    phone_number = st.text_input(
        "Номер телефона",
        placeholder="+996...",
        value="",
    )
    phone_number = norm_phone(phone_number)

    labels, mapping = extract_manager_choices(clients)

    manager_value: str | None = None

    if labels:
        chosen_label = st.selectbox(
            "Менеджер",
            options=["—"] + labels,
            index=0,
        )

        if chosen_label != "—":
            manager_value = mapping[chosen_label]

    else:
        manager_value = (
            st.text_input(
                "Менеджер (имя или ID)",
                placeholder="Например: Нурбек или 3",
            ).strip()
            or None
        )

    comment = st.text_area(
        "Комментарий",
        placeholder="Любые заметки по клиенту",
        height=110,
    )

    username = ""
    if first_name or last_name:
        username = f"{last_name} {first_name}".strip()

    confirm = st.checkbox("Подтверждаю выбор кода и данных", value=False)

    if confirm:
        params: dict[str, str] = {
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

        admin_url = build_admin_url(params)

        try:
            st.link_button(
                "Перейти в админку и создать клиента",
                admin_url,
                use_container_width=True,
            )
        except TypeError:
            st.link_button(
                "Перейти в админку и создать клиента",
                admin_url,
            )

    else:
        st.warning("Поставьте подтверждение, чтобы активировать переход.")