import streamlit as st

import auth
import db
import ui

ui.setup("게시판", "📝")

user = auth.current_user()

# ------------------------------ 글쓰기 (로그인한 회원만)
if user is None:
    st.info("글을 쓰려면 사이드바의 '회원가입 로그인' 페이지에서 먼저 로그인하세요. 읽기는 누구나 할 수 있습니다.")
else:
    with st.expander("✏️ 새 글 쓰기"):
        with st.form("post_form", clear_on_submit=True):
            title = st.text_input("제목", max_chars=80, key="post_title")
            body = st.text_area("내용", height=150, key="post_body")
            submitted = st.form_submit_button("등록", type="primary")
        if submitted:
            if not title.strip() or not body.strip():
                st.error("제목과 내용을 모두 입력하세요.")
            else:
                db.execute(
                    "INSERT INTO posts (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
                    (user["id"], title.strip(), body.strip(), db.now()),
                )
                ui.flash("글을 등록했습니다.")
                st.rerun()

# ------------------------------ 글 목록
posts = db.query(
    """
    SELECT posts.id, posts.title, posts.body, posts.created_at, posts.user_id, users.username
    FROM posts JOIN users ON users.id = posts.user_id
    ORDER BY posts.id DESC
    """
)

st.subheader(f"전체 글 {len(posts)} 개")
if not posts:
    st.write("아직 글이 없습니다.")

for post in posts:
    with st.container(border=True):
        st.markdown(f"**{post['title']}**")
        st.caption(f"{post['username']} · {post['created_at']}")
        # 다른 회원이 쓴 글이므로 마크다운이나 HTML 로 해석하지 않고 글자 그대로 보여 준다.
        st.text(post["body"])
        if user and user["id"] == post["user_id"]:
            if st.button("삭제", key=f"delete_post_{post['id']}"):
                db.execute("DELETE FROM posts WHERE id = ? AND user_id = ?", (post["id"], user["id"]))
                ui.flash("글을 삭제했습니다.")
                st.rerun()
