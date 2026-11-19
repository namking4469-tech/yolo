import io

import numpy as np
import pandas as pd
import streamlit as st

import ui

ui.setup("CSV 업로드 분석", "📂", layout="wide")


def read_csv(raw: bytes) -> pd.DataFrame:
    """한글 CSV 는 UTF-8 또는 CP949(엑셀 저장본)인 경우가 많아 차례로 시도한다."""
    for encoding in ("utf-8-sig", "cp949"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("UTF-8 또는 CP949 로 읽을 수 없는 파일입니다.")


@st.cache_data
def sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    n = 60
    return pd.DataFrame(
        {
            "이름": [f"학생{i:02d}" for i in range(1, n + 1)],
            "반": rng.choice(["1반", "2반", "3반"], n),
            "국어": rng.integers(40, 101, n),
            "영어": rng.integers(40, 101, n),
            "수학": rng.integers(30, 101, n),
        }
    )


uploaded = st.file_uploader("CSV 파일을 올리세요", type="csv", key="csv_file")

if uploaded is not None:
    try:
        df = read_csv(uploaded.getvalue())
    except (ValueError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        st.error(f"파일을 읽지 못했습니다: {exc}")
        st.stop()
    st.success(f"'{uploaded.name}' 을(를) 읽었습니다.")
else:
    st.info("파일을 올리지 않아 예시 성적표를 보여 줍니다.")
    df = sample_data()

c1, c2, c3 = st.columns(3)
c1.metric("행", f"{len(df):,}")
c2.metric("열", f"{df.shape[1]:,}")
c3.metric("빈 칸", f"{int(df.isna().sum().sum()):,}")

tab_data, tab_stats, tab_chart = st.tabs(["데이터", "통계", "차트"])

with tab_data:
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button(
        "CSV 로 내려받기",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="data.csv",
        mime="text/csv",
    )

numeric = df.select_dtypes("number").columns.tolist()

with tab_stats:
    if numeric:
        st.dataframe(df[numeric].describe().T, width="stretch")
    else:
        st.write("숫자 열이 없습니다.")

with tab_chart:
    if not numeric:
        st.write("숫자 열이 없어 차트를 그릴 수 없습니다.")
    else:
        others = [c for c in df.columns if c not in numeric]
        y = st.multiselect("값 (숫자 열)", numeric, default=numeric[:1], key="chart_y")
        group = st.selectbox("묶을 기준", ["(묶지 않음)"] + others, key="chart_group")
        if not y:
            st.write("값으로 쓸 열을 하나 이상 고르세요.")
        elif group == "(묶지 않음)":
            st.line_chart(df[y])
        else:
            st.caption(f"'{group}' 별 평균")
            st.bar_chart(df.groupby(group)[y].mean())
