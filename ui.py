"""모든 샘플 페이지가 함께 쓰는 화면 도우미."""

import streamlit as st

import auth


def setup(title: str, icon: str, layout: str = "centered") -> None:
    """페이지 설정, 사이드바 로그인 상태, 제목, 알림 메시지를 한 번에 처리한다."""
    st.set_page_config(page_title=title, page_icon=icon, layout=layout)
    user = auth.current_user()
    with st.sidebar:
        if user:
            st.success(f"👤 {user['username']} 님 로그인 중")
            st.button("로그아웃", key="sidebar_logout", on_click=auth.logout)
        else:
            st.info("로그인하지 않았습니다.")
    st.title(f"{icon} {title}")
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message)


def flash(message: str) -> None:
    """다음 화면이 그려질 때 한 번 보여 줄 성공 메시지를 저장한다."""
    st.session_state.flash = message
