import time

import pandas as pd
import streamlit as st

import ui

ui.setup("캐시 있음 vs 없음", "⚡", layout="wide")
st.write(
    "같은 '느린 계산'을 캐시 없이 한 번, 캐시를 붙여 한 번 실행해서 걸린 시간을 비교합니다. "
    "같은 숫자로 여러 번 실행해 보세요."
)

DELAY = 2.0  # 느린 작업을 흉내 내려고 일부러 기다리는 시간(초)


def slow_sum_of_squares(n: int) -> int:
    """오래 걸리는 계산을 흉내 낸다: 2초 기다린 뒤 1² + 2² + … + n² 을 돌려준다."""
    time.sleep(DELAY)
    return sum(i * i for i in range(n + 1))


def without_cache(n: int) -> int:
    return slow_sum_of_squares(n)


@st.cache_data(show_spinner=False)
def with_cache(n: int) -> int:
    # 같은 n 으로 다시 부르면 함수 본문을 실행하지 않고 저장해 둔 결과를 바로 돌려준다.
    return slow_sum_of_squares(n)


history = st.session_state.setdefault("cache_history", [])


def measure(kind: str, func, n: int) -> None:
    start = time.perf_counter()
    result = func(n)
    elapsed = time.perf_counter() - start
    history.append(
        {
            "회차": len(history) + 1,
            "방식": kind,
            "입력 n": n,
            "결과": result,
            "걸린 시간(초)": round(elapsed, 3),
            # 기다리는 시간보다 훨씬 빨리 끝났다면 함수 본문이 실행되지 않은 것이다.
            "실제 계산": "아니요 (저장된 결과)" if elapsed < DELAY / 2 else "예",
        }
    )


# ------------------------------ 실행 버튼
n = st.number_input("입력 n", min_value=1, max_value=1_000_000, value=1000, step=1, key="cache_n")

b1, b2, b3, b4, b5 = st.columns(5)
run_plain = b1.button("🐢 캐시 없이 실행", width="stretch")
run_cached = b2.button("⚡ 캐시로 실행", width="stretch")
run_both = b3.button("둘 다 실행", type="primary", width="stretch")
if b4.button("캐시 비우기", width="stretch"):
    with_cache.clear()
    st.toast("캐시를 비웠습니다. 다음 '캐시로 실행'은 다시 계산합니다.")
if b5.button("기록 지우기", width="stretch"):
    history.clear()

if run_plain or run_both:
    with st.spinner("캐시 없이 계산하는 중…"):
        measure("캐시 없음", without_cache, int(n))
if run_cached or run_both:
    with st.spinner("캐시로 계산하는 중…"):
        measure("캐시 있음", with_cache, int(n))

# ------------------------------ 나란히 비교
left, right = st.columns(2, gap="large")


def show_side(column, kind: str, icon: str, code: str) -> None:
    rows = [row for row in history if row["방식"] == kind]
    with column.container(border=True):
        st.subheader(f"{icon} {kind}")
        st.code(code, language="python")
        if not rows:
            st.write("아직 실행하지 않았습니다.")
            return
        last = rows[-1]
        m1, m2, m3 = st.columns(3)
        m1.metric("마지막 실행", f"{last['걸린 시간(초)']:.3f} 초")
        m2.metric("실행 횟수", f"{len(rows)} 번")
        m3.metric("실제로 계산한 횟수", f"{sum(row['실제 계산'] == '예' for row in rows)} 번")
        st.caption(f"n = {last['입력 n']:,} 의 결과: {last['결과']:,}")


show_side(left, "캐시 없음", "🐢", "def without_cache(n):\n    return slow_sum_of_squares(n)")
show_side(right, "캐시 있음", "⚡", "@st.cache_data\ndef with_cache(n):\n    return slow_sum_of_squares(n)")

# ------------------------------ 기록
if history:
    df = pd.DataFrame(history)
    totals = df.groupby("방식")["걸린 시간(초)"].sum()
    if len(totals) == 2 and totals["캐시 있음"] < totals["캐시 없음"]:
        saved = totals["캐시 없음"] - totals["캐시 있음"]
        st.success(
            f"지금까지 캐시 없음은 모두 {totals['캐시 없음']:.1f}초, 캐시 있음은 {totals['캐시 있음']:.1f}초 걸렸습니다. "
            f"차이는 {saved:.1f}초입니다."
        )

    st.subheader("실행 기록")
    chart_col, table_col = st.columns(2)
    chart_col.bar_chart(df, x="회차", y="걸린 시간(초)", color="방식", height=300)
    table_col.dataframe(df, hide_index=True, width="stretch", height=300)

with st.expander("캐시는 어떻게 동작하나요?"):
    st.markdown(
        f"""
- **캐시 없음**: 버튼을 누를 때마다 함수 본문이 실행되어 매번 약 {DELAY:g}초가 걸립니다.
- **캐시 있음**: `@st.cache_data` 가 입력값과 결과를 짝지어 저장합니다.
  처음 보는 `n` 이면 계산하느라 약 {DELAY:g}초가 걸리고, 같은 `n` 을 다시 넣으면 저장된 결과를 바로 돌려줍니다.
- `n` 을 바꾸면 새 입력이므로 캐시가 있어도 한 번은 다시 계산합니다.
- **캐시 비우기**를 누르면 저장된 결과가 지워져 다음 실행은 다시 계산합니다.
- 캐시는 서버에 저장되어 모든 방문자가 함께 씁니다. 다른 사람이 이미 계산한 `n` 은 내 첫 실행에서도 빠를 수 있습니다.
"""
    )
