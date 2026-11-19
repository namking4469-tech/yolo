import numpy as np
import pandas as pd
import streamlit as st

import ui

ui.setup("매출 대시보드", "📊", layout="wide")
st.caption("난수로 만든 예시 데이터입니다. 실제 매출이 아닙니다.")

REGIONS = ["서울", "부산", "대구", "광주", "제주"]
CATEGORIES = ["과일", "음료", "과자", "문구", "전자"]


@st.cache_data
def load_sales() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    index = pd.MultiIndex.from_product([dates, REGIONS, CATEGORIES], names=["date", "region", "category"])
    df = index.to_frame(index=False)
    df["orders"] = rng.poisson(20, len(df)) + (df["date"].dt.dayofweek >= 5) * 8
    df["sales"] = df["orders"] * rng.integers(3000, 15000, len(df))
    return df


sales = load_sales()

with st.sidebar:
    st.header("필터")
    regions = st.multiselect("지역", REGIONS, default=REGIONS, key="dash_regions")
    categories = st.multiselect("분류", CATEGORIES, default=CATEGORIES, key="dash_categories")
    first, last = sales["date"].min().date(), sales["date"].max().date()
    start, end = st.slider("기간", first, last, (first, last), key="dash_period")

view = sales[
    sales["region"].isin(regions)
    & sales["category"].isin(categories)
    & sales["date"].between(pd.Timestamp(start), pd.Timestamp(end))
]

if view.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다. 필터를 바꿔 보세요.")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("총 매출", f"{view['sales'].sum() / 1e8:,.1f} 억 원")
m2.metric("주문 수", f"{view['orders'].sum():,} 건")
m3.metric("주문당 매출", f"{view['sales'].sum() / view['orders'].sum():,.0f} 원")
best = view.groupby("region")["sales"].sum().idxmax()
m4.metric("매출 1위 지역", best)

st.subheader("지역별 주간 매출")
weekly = view.pivot_table(index=pd.Grouper(key="date", freq="W"), columns="region", values="sales", aggfunc="sum")
st.line_chart(weekly)

left, right = st.columns(2)
with left:
    st.subheader("분류별 매출")
    st.bar_chart(view.groupby("category")["sales"].sum())
with right:
    st.subheader("월별 주문 수")
    monthly = view.assign(month=view["date"].dt.strftime("%Y-%m")).pivot_table(
        index="month", columns="category", values="orders", aggfunc="sum"
    )
    st.area_chart(monthly)

st.subheader("지역 × 분류 매출표")
table = view.pivot_table(index="region", columns="category", values="sales", aggfunc="sum")
st.dataframe(table.style.format("{:,.0f}"), width="stretch")
