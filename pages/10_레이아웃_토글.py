import numpy as np
import pandas as pd
import streamlit as st

import ui

ui.setup("사이드바 · 화면 분할 · 토글", "🧩", layout="wide")
st.caption("사이드바에서 화면 분할 방식과 보여 줄 정보를 고르세요. 표시되는 값은 모두 예시 데이터입니다.")

# ---------------------------------------------------------------
# 정보 패널: 각 패널은 화면의 한 칸에 그려지는 함수다.
# ---------------------------------------------------------------


def panel_profile():
    st.subheader("👤 프로필")
    c1, c2 = st.columns([1, 3])
    c1.html('<div style="font-size:64px; text-align:center;">🧙</div>')
    c2.write("**마법사 루미**")
    c2.caption("별빛 마법을 쓰는 꼬마 마법사")
    if st.toggle("자세히 보기", key="profile_more"):
        st.write("- 레벨: 12\n- 직업: 마법사\n- 특기: 별빛 화살\n- 좋아하는 것: 풍선 🎈")


def panel_weather():
    st.subheader("🌤️ 날씨")
    fahrenheit = st.toggle("화씨(°F)로 보기", key="weather_f")
    cities = {"서울": 12, "부산": 16, "제주": 18}
    for col, (city, celsius) in zip(st.columns(len(cities)), cities.items()):
        value = f"{celsius * 9 / 5 + 32:.0f} °F" if fahrenheit else f"{celsius} °C"
        col.metric(city, value)


def panel_todo():
    st.subheader("✅ 할 일")
    todos = ["conda 환경 만들기", "Streamlit 설치", "페이지 만들기", "친구에게 자랑하기"]
    hide_done = st.toggle("끝낸 일 숨기기", key="todo_hide")
    # 숨긴 체크박스는 위젯 상태가 사라지므로, 완료 여부는 따로 저장해 둔다.
    done = st.session_state.setdefault("todo_done", [True, True, False, False])

    def remember(i):
        done[i] = st.session_state[f"todo_{i}"]

    for i, todo in enumerate(todos):
        if hide_done and done[i]:
            continue
        st.checkbox(todo, value=done[i], key=f"todo_{i}", on_change=remember, args=(i,))
    st.progress(sum(done) / len(todos), text=f"{sum(done)} / {len(todos)} 완료")


def panel_chart():
    st.subheader("📈 방문자 수")
    rng = np.random.default_rng(3)
    data = pd.DataFrame(
        {"방문자": rng.integers(80, 200, 14), "가입자": rng.integers(5, 40, 14)},
        index=pd.date_range("2026-11-01", periods=14).strftime("%m-%d"),
    )
    as_table = st.toggle("표로 보기", key="chart_table")
    if as_table:
        st.dataframe(data, width="stretch", height=240)
    else:
        st.line_chart(data, height=240)


def panel_notice():
    st.subheader("📢 공지사항")
    notices = {
        "🎈 풍선 축제가 열립니다": "이번 주말, 풍선과 괴물 나라에서 풍선 축제가 열립니다. 누구나 참여할 수 있어요.",
        "🛠️ 정기 점검 안내": "매주 수요일 새벽 2시부터 4시까지 서버 점검이 있습니다.",
        "👾 새 괴물 등장": "외계 문어가 새로 나타났습니다. 조심하세요!",
    }
    for title, body in notices.items():
        with st.expander(title):
            st.write(body)


def panel_code():
    st.subheader("💻 이 페이지의 핵심 코드")
    with st.popover("토글 쓰는 법"):
        st.code('if st.toggle("자세히 보기"):\n    st.write("숨겨 둔 내용")', language="python")
    tab_sidebar, tab_columns = st.tabs(["사이드바", "화면 분할"])
    tab_sidebar.code('with st.sidebar:\n    show = st.toggle("프로필", value=True)', language="python")
    tab_columns.code("left, right = st.columns([2, 1])\nleft.write('왼쪽')\nright.write('오른쪽')", language="python")


PANELS = {
    "👤 프로필": panel_profile,
    "🌤️ 날씨": panel_weather,
    "✅ 할 일": panel_todo,
    "📈 방문자 수": panel_chart,
    "📢 공지사항": panel_notice,
    "💻 코드": panel_code,
}

LAYOUTS = {
    "1단 (분할 없음)": [1],
    "2단 (1 : 1)": [1, 1],
    "2단 (2 : 1)": [2, 1],
    "2단 (1 : 2)": [1, 2],
    "3단 (1 : 1 : 1)": [1, 1, 1],
}

# ---------------------------------------------------------------
# 사이드바: 화면 분할 방식과 패널별 표시 여부
# ---------------------------------------------------------------
with st.sidebar:
    st.header("🧩 화면 설정")
    layout_name = st.radio("화면 분할", list(LAYOUTS), index=1, key="layout_name")
    bordered = st.toggle("테두리 표시", value=True, key="layout_border")

    st.header("👁️ 보여 줄 정보")
    visible = [name for name in PANELS if st.toggle(name, value=True, key=f"show_{name}")]

# ---------------------------------------------------------------
# 본문: 켜진 패널을 칸마다 차례로 나눠 담는다.
# ---------------------------------------------------------------
if not visible:
    st.info("사이드바에서 보여 줄 정보를 하나 이상 켜세요.")
    st.stop()

columns = st.columns(LAYOUTS[layout_name], gap="medium")
for i, name in enumerate(visible):
    with columns[i % len(columns)]:
        with st.container(border=bordered):
            PANELS[name]()
