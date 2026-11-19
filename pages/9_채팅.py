import random
from datetime import datetime

import streamlit as st

import auth
import ui

ui.setup("채팅 화면", "💬")
st.caption("정해진 규칙으로만 대답하는 간단한 봇입니다. AI 모델은 연결되어 있지 않습니다.")

user = auth.current_user()
nickname = user["username"] if user else "손님"

RULES = [
    (("안녕", "hello", "hi"), lambda: f"안녕하세요, {nickname} 님! 👋"),
    (("시간", "몇 시"), lambda: f"지금은 {datetime.now():%H시 %M분} 입니다. ⏰"),
    (("날짜", "오늘"), lambda: f"오늘은 {datetime.now():%Y년 %m월 %d일} 입니다. 📅"),
    (("주사위",), lambda: f"🎲 주사위를 굴렸더니 {random.randint(1, 6)} 이(가) 나왔어요."),
    (("동전",), lambda: f"🪙 {random.choice(['앞면', '뒷면'])} 입니다."),
    (("이름", "누구"), lambda: "저는 Streamlit 으로 만든 연습용 봇이에요. 🤖"),
    (("도움", "help"), lambda: "이런 말을 알아들어요: 안녕, 시간, 날짜, 주사위, 동전, 이름"),
]


def reply(text: str) -> str:
    lowered = text.lower()
    for keywords, answer in RULES:
        if any(keyword in lowered for keyword in keywords):
            return answer()
    return f"'{text}' 라고 하셨군요. '도움' 이라고 입력하면 제가 아는 말을 알려 드려요."


if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "content": "안녕하세요! '도움' 이라고 입력해 보세요."}]

if st.sidebar.button("대화 지우기", key="chat_clear"):
    del st.session_state.chat
    st.rerun()

for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("메시지를 입력하세요")
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    answer = reply(prompt)
    st.session_state.chat.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)
