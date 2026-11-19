import sqlite3

import pandas as pd
import streamlit as st

import db
import ui

ui.setup("데이터베이스 CRUD", "🗄️", layout="wide")
st.caption(f"SQLite 파일: {db.DB_PATH}")

tab_list, tab_add, tab_edit, tab_sql = st.tabs(["조회", "추가", "수정 · 삭제", "SQL 실행"])

# ------------------------------ 조회 (Read)
with tab_list:
    c1, c2 = st.columns([2, 3])
    keyword = c1.text_input("상품명 검색", key="search_keyword")
    chosen = c2.multiselect("분류", db.CATEGORIES, key="search_categories")

    sql = "SELECT id, name, category, price, stock FROM products WHERE name LIKE ?"
    params = [f"%{keyword}%"]
    if chosen:
        sql += f" AND category IN ({','.join('?' * len(chosen))})"
        params += chosen
    rows = db.query(sql + " ORDER BY id", tuple(params))
    df = pd.DataFrame(rows, columns=["id", "name", "category", "price", "stock"])

    m1, m2, m3 = st.columns(3)
    m1.metric("상품 수", f"{len(df)} 개")
    m2.metric("총 재고", f"{int(df['stock'].sum()):,} 개")
    m3.metric("재고 금액", f"{int((df['price'] * df['stock']).sum()):,} 원")

    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
        column_config={
            "id": "번호",
            "name": "상품명",
            "category": "분류",
            "price": st.column_config.NumberColumn("가격", format="%d 원"),
            "stock": st.column_config.ProgressColumn("재고", min_value=0, max_value=500, format="%d"),
        },
    )

# ------------------------------ 추가 (Create)
with tab_add:
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("상품명", key="add_name")
        category = st.selectbox("분류", db.CATEGORIES, key="add_category")
        price = st.number_input("가격(원)", min_value=0, step=100, value=1000, key="add_price")
        stock = st.number_input("재고", min_value=0, step=1, value=10, key="add_stock")
        submitted = st.form_submit_button("추가", type="primary")
    if submitted:
        if not name.strip():
            st.error("상품명을 입력하세요.")
        else:
            new_id = db.execute(
                "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
                (name.strip(), category, int(price), int(stock)),
            )
            ui.flash(f"{new_id}번 상품 '{name.strip()}' 을(를) 추가했습니다.")
            st.rerun()

# ------------------------------ 수정 · 삭제 (Update / Delete)
with tab_edit:
    products = db.query("SELECT * FROM products ORDER BY id")
    if not products:
        st.info("상품이 없습니다. '추가' 탭에서 먼저 등록하세요.")
    else:
        by_id = {p["id"]: p for p in products}
        pid = st.selectbox(
            "상품 선택",
            list(by_id),
            format_func=lambda i: f"{i}. {by_id[i]['name']}",
            key="edit_id",
        )
        item = by_id[pid]
        # key 에 상품 번호를 넣어야 다른 상품을 고를 때 입력값이 새로 채워진다.
        with st.form(f"edit_form_{pid}"):
            name = st.text_input("상품명", value=item["name"], key=f"edit_name_{pid}")
            category = st.selectbox(
                "분류",
                db.CATEGORIES,
                index=db.CATEGORIES.index(item["category"]) if item["category"] in db.CATEGORIES else 0,
                key=f"edit_category_{pid}",
            )
            price = st.number_input("가격(원)", min_value=0, step=100, value=item["price"], key=f"edit_price_{pid}")
            stock = st.number_input("재고", min_value=0, step=1, value=item["stock"], key=f"edit_stock_{pid}")
            b1, b2, _ = st.columns([1, 1, 5])
            save = b1.form_submit_button("저장", type="primary")
            remove = b2.form_submit_button("삭제")
        if save:
            if not name.strip():
                st.error("상품명을 입력하세요.")
            else:
                db.execute(
                    "UPDATE products SET name = ?, category = ?, price = ?, stock = ? WHERE id = ?",
                    (name.strip(), category, int(price), int(stock), pid),
                )
                ui.flash(f"{pid}번 상품을 수정했습니다.")
                st.rerun()
        if remove:
            db.execute("DELETE FROM products WHERE id = ?", (pid,))
            ui.flash(f"{pid}번 상품 '{item['name']}' 을(를) 삭제했습니다.")
            st.rerun()

# ------------------------------ SQL 직접 실행 (읽기 전용)
with tab_sql:
    st.write("읽기 전용으로 실행됩니다. 테이블: `users`, `products`, `posts`")
    sql_text = st.text_area(
        "SQL",
        "SELECT category AS 분류, COUNT(*) AS 상품수, SUM(stock) AS 재고합계\n"
        "FROM products\nGROUP BY category\nORDER BY 재고합계 DESC;",
        height=140,
        key="sql_text",
    )
    if st.button("실행", key="sql_run"):
        try:
            columns, result = db.read_only_query(sql_text)
        except (sqlite3.Error, sqlite3.Warning) as exc:
            st.error(f"SQL 오류: {exc}")
        else:
            st.dataframe(pd.DataFrame(result, columns=columns), hide_index=True, width="stretch")
            st.caption(f"{len(result)} 행 (최대 500 행까지 표시)")
