from datetime import date, time

import streamlit as st

import ui

ui.setup("입력 폼 모음", "🧾")
st.write("Streamlit 의 여러 입력 위젯을 한 폼에 모은 예제입니다. 제출하면 입력값을 아래에 보여 줍니다.")

with st.form("survey_form"):
    st.subheader("기본 정보")
    c1, c2 = st.columns(2)
    name = c1.text_input("이름", key="f_name")
    age = c2.number_input("나이", min_value=1, max_value=120, value=20, key="f_age")
    birthday = c1.date_input("생일", value=date(2000, 1, 1), min_value=date(1900, 1, 1), key="f_birthday")
    wake_up = c2.time_input("기상 시간", value=time(7, 0), key="f_wake")

    st.subheader("취향")
    language = st.selectbox("가장 좋아하는 언어", ["Python", "JavaScript", "Java", "C++", "Go", "Rust"], key="f_lang")
    hobbies = st.multiselect("취미", ["독서", "게임", "운동", "요리", "여행", "음악"], default=["게임"], key="f_hobby")
    level = st.radio("코딩 실력", ["입문", "초급", "중급", "고급"], horizontal=True, key="f_level")
    satisfaction = st.slider("Streamlit 만족도", 0, 10, 8, key="f_score")
    budget = st.slider("한 달 책값 (만 원)", 0, 50, (5, 15), key="f_budget")
    color = st.color_picker("좋아하는 색", "#3498db", key="f_color")

    st.subheader("기타")
    memo = st.text_area("하고 싶은 말", key="f_memo")
    newsletter = st.toggle("소식 받기", key="f_news")
    agreed = st.checkbox("입력한 내용이 맞습니다.", key="f_agree")

    submitted = st.form_submit_button("제출", type="primary")

if submitted:
    if not name.strip():
        st.error("이름을 입력하세요.")
    elif not agreed:
        st.error("확인란에 체크하세요.")
    else:
        st.success(f"{name.strip()} 님, 제출해 주셔서 감사합니다!")
        st.html(
            f'<div style="height:14px; border-radius:7px; background:{color};"></div>'
        )
        st.json(
            {
                "이름": name.strip(),
                "나이": age,
                "생일": str(birthday),
                "기상 시간": wake_up.strftime("%H:%M"),
                "언어": language,
                "취미": hobbies,
                "실력": level,
                "만족도": satisfaction,
                "책값 범위(만 원)": list(budget),
                "색": color,
                "메모": memo,
                "소식 받기": newsletter,
            }
        )
