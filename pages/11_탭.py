import numpy as np
import pandas as pd
import streamlit as st

import ui

ui.setup("탭 모음", "🗂️", layout="wide")
st.caption("탭 8개에 서로 다른 내용을 담은 예제입니다. 표시되는 값은 모두 예시 데이터입니다.")

(
    tab_home,
    tab_text,
    tab_chart,
    tab_table,
    tab_calc,
    tab_color,
    tab_map,
    tab_faq,
) = st.tabs(["🏠 홈", "📝 글", "📊 차트", "📋 표", "🧮 계산기", "🎨 색상", "🗺️ 지도", "❓ FAQ"])

# ------------------------------ 1. 홈
with tab_home:
    st.subheader("탭 페이지에 오신 것을 환영합니다")
    st.write("위쪽의 탭을 누르면 화면이 바뀝니다. 탭마다 다른 종류의 Streamlit 기능을 담았습니다.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("탭 수", "8 개")
    c2.metric("방문자", "1,234 명", "+56")
    c3.metric("가입자", "89 명", "+7")
    c4.metric("오류", "2 건", "-3", delta_color="inverse")
    st.info("탭은 `st.tabs([...])` 로 만들고, `with 탭:` 안에 내용을 넣습니다.")

# ------------------------------ 2. 글
with tab_text:
    left, right = st.columns(2)
    with left:
        st.subheader("마크다운")
        st.markdown(
            """
**굵게**, *기울임*, ~~취소선~~, `코드`, :blue[색 글자]

1. 탭을 만든다
2. 내용을 넣는다
3. 실행한다

> 탭은 많은 내용을 좁은 화면에 정리할 때 좋습니다.
"""
        )
    with right:
        st.subheader("알림 상자")
        st.success("성공 메시지")
        st.info("안내 메시지")
        st.warning("경고 메시지")
        st.error("오류 메시지")

# ------------------------------ 3. 차트
with tab_chart:
    rng = np.random.default_rng(11)
    data = pd.DataFrame(
        rng.integers(10, 100, (12, 3)),
        columns=["사과", "바나나", "포도"],
        index=[f"{m:02d}월" for m in range(1, 13)],
    )
    kind = st.radio("차트 종류", ["선", "막대", "영역"], horizontal=True, key="tab_chart_kind")
    fruits = st.multiselect("과일", list(data.columns), default=list(data.columns), key="tab_chart_fruits")
    if not fruits:
        st.warning("과일을 하나 이상 고르세요.")
    elif kind == "선":
        st.line_chart(data[fruits])
    elif kind == "막대":
        st.bar_chart(data[fruits])
    else:
        st.area_chart(data[fruits])

# ------------------------------ 4. 표
with tab_table:
    st.write("칸을 눌러 직접 고칠 수 있고, 맨 아래에서 행을 추가할 수 있습니다. (저장되지는 않습니다)")
    scores = pd.DataFrame(
        {
            "이름": ["철수", "영희", "민수", "지은"],
            "국어": [90, 85, 70, 95],
            "수학": [80, 95, 65, 88],
            "합격": [True, True, False, True],
        }
    )
    edited = st.data_editor(scores, num_rows="dynamic", hide_index=True, width="stretch", key="tab_table_editor")
    numbers = edited[["국어", "수학"]].apply(pd.to_numeric, errors="coerce")
    m1, m2, m3 = st.columns(3)
    m1.metric("학생 수", f"{len(edited)} 명")
    m2.metric("국어 평균", "-" if numbers["국어"].dropna().empty else f"{numbers['국어'].mean():.1f}")
    m3.metric("수학 평균", "-" if numbers["수학"].dropna().empty else f"{numbers['수학'].mean():.1f}")

# ------------------------------ 5. 계산기
with tab_calc:
    c1, c2, c3 = st.columns([2, 1, 2])
    a = c1.number_input("첫째 수", value=10.0, key="calc_a")
    op = c2.selectbox("연산", ["+", "-", "×", "÷"], key="calc_op")
    b = c3.number_input("둘째 수", value=3.0, key="calc_b")
    if op == "÷" and b == 0:
        st.error("0 으로 나눌 수 없습니다.")
    else:
        result = {"+": a + b, "-": a - b, "×": a * b, "÷": a / b if b else 0}[op]
        st.metric("결과", f"{a:g} {op} {b:g} = {result:g}")

# ------------------------------ 6. 색상
with tab_color:
    c1, c2 = st.columns([1, 3])
    color = c1.color_picker("색 고르기", "#8e44ad", key="tab_color_value")
    size = c1.slider("둥글기", 0, 60, 16, key="tab_color_radius")
    r, g, b_ = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    # 밝은 색 위에는 검은 글자, 어두운 색 위에는 흰 글자를 쓴다.
    text = "#000000" if (r * 299 + g * 587 + b_ * 114) / 1000 > 150 else "#ffffff"
    c2.html(
        f'<div style="background:{color}; color:{text}; border-radius:{size}px; padding:48px;'
        f' text-align:center; font-size:22px;">{color.upper()} · rgb({r}, {g}, {b_})</div>'
    )

# ------------------------------ 7. 지도
with tab_map:
    st.write("주요 도시 위치입니다. 지도 배경은 인터넷에서 불러옵니다.")
    cities = pd.DataFrame(
        {
            "도시": ["서울", "부산", "대구", "광주", "대전", "제주"],
            "lat": [37.5665, 35.1796, 35.8714, 35.1595, 36.3504, 33.4996],
            "lon": [126.9780, 129.0756, 128.6014, 126.8526, 127.3845, 126.5312],
        }
    )
    left, right = st.columns([3, 1])
    left.map(cities, latitude="lat", longitude="lon", size=8000, zoom=6)
    right.dataframe(cities, hide_index=True, width="stretch")

# ------------------------------ 8. FAQ
with tab_faq:
    faq = {
        "탭은 몇 개까지 만들 수 있나요?": "개수 제한은 없지만, 화면 너비를 넘으면 좌우로 넘겨 봐야 해서 10개 안쪽이 보기 좋습니다.",
        "탭을 바꾸면 입력한 값이 사라지나요?": "아니요. 모든 탭의 내용은 한 번에 그려지고, 탭은 보이는 부분만 바꿉니다.",
        "처음 열릴 탭을 정할 수 있나요?": "기본은 첫 번째 탭입니다. 가장 중요한 내용을 맨 앞에 두세요.",
        "탭과 사이드바 페이지는 어떻게 다른가요?": "탭은 한 파일 안에서 화면을 나누고, 사이드바 페이지는 파일 하나가 페이지 하나입니다.",
    }
    for question, answer in faq.items():
        with st.expander(question):
            st.write(answer)
