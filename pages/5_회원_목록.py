import pandas as pd
import streamlit as st

import auth
import db
import ui

ui.setup("회원 목록", "👥")

if auth.current_user() is None:
    st.warning("회원만 볼 수 있는 페이지입니다. 사이드바의 '회원가입 로그인' 페이지에서 로그인하세요.")
    st.stop()

# 비밀번호 해시와 솔트는 화면에 내보내지 않는다.
users = db.query(
    """
    SELECT users.id, users.username, users.email, users.created_at, COUNT(posts.id) AS post_count
    FROM users LEFT JOIN posts ON posts.user_id = users.id
    GROUP BY users.id
    ORDER BY users.id
    """
)
df = pd.DataFrame(users, columns=["id", "username", "email", "created_at", "post_count"])

c1, c2 = st.columns(2)
c1.metric("전체 회원", f"{len(df)} 명")
c2.metric("전체 게시글", f"{int(df['post_count'].sum())} 개")

st.dataframe(
    df,
    hide_index=True,
    width="stretch",
    column_config={
        "id": "번호",
        "username": "아이디",
        "email": "이메일",
        "created_at": "가입 일시",
        "post_count": "게시글 수",
    },
)

st.subheader("날짜별 가입자 수")
st.bar_chart(df.assign(day=df["created_at"].str[:10]).groupby("day").size().rename("가입자 수"))
