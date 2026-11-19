import streamlit as st

import auth
import ui

ui.setup("회원가입 · 로그인", "🔐")

user = auth.current_user()

if user is None:
    tab_login, tab_signup = st.tabs(["로그인", "회원가입"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("아이디", key="login_username")
            password = st.text_input("비밀번호", type="password", key="login_password")
            submitted = st.form_submit_button("로그인", type="primary")
        if submitted:
            if auth.login(username, password):
                ui.flash(f"{username} 님, 환영합니다!")
                st.rerun()
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("아이디", key="signup_username", help="3~20자의 한글, 영문, 숫자, 밑줄")
            new_email = st.text_input("이메일", key="signup_email", placeholder="name@example.com")
            new_password = st.text_input(
                "비밀번호", type="password", key="signup_password", help=f"{auth.MIN_PASSWORD}자 이상"
            )
            new_confirm = st.text_input("비밀번호 확인", type="password", key="signup_confirm")
            agreed = st.checkbox("이용 약관에 동의합니다.", key="signup_agree")
            submitted = st.form_submit_button("회원가입", type="primary")
        if submitted:
            errors = [] if agreed else ["이용 약관에 동의해야 합니다."]
            errors = errors or auth.signup(new_username, new_email, new_password, new_confirm)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("가입이 완료되었습니다. '로그인' 탭에서 로그인하세요.")

else:
    st.subheader("내 정보")
    c1, c2, c3 = st.columns(3)
    c1.metric("아이디", user["username"])
    c2.metric("회원 번호", user["id"])
    c3.metric("가입일", user["created_at"][:10])
    st.write(f"이메일: {user['email']}")

    st.button("로그아웃", on_click=auth.logout)

    with st.expander("비밀번호 변경"):
        with st.form("password_form", clear_on_submit=True):
            old = st.text_input("현재 비밀번호", type="password", key="pw_old")
            new = st.text_input("새 비밀번호", type="password", key="pw_new")
            confirm = st.text_input("새 비밀번호 확인", type="password", key="pw_confirm")
            submitted = st.form_submit_button("변경")
        if submitted:
            errors = auth.change_password(user, old, new, confirm)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("비밀번호를 변경했습니다.")

    with st.expander("회원 탈퇴"):
        st.warning("탈퇴하면 계정과 내가 쓴 게시글이 모두 삭제되며 되돌릴 수 없습니다.")
        sure = st.checkbox("위 내용을 확인했습니다.", key="delete_sure")
        if st.button("탈퇴하기", disabled=not sure):
            auth.delete_account(user)
            ui.flash("탈퇴 처리되었습니다.")
            st.rerun()
