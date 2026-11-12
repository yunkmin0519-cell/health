
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data import generate_health_data, add_age_group


# 페이지 설정
st.set_page_config(
    page_title="건강 데이터 분석",
    page_icon="📊",
    layout="wide"
)

# 데이터 불러오기
if "health_data" not in st.session_state:
    st.session_state.health_data = generate_health_data(1000)

df = st.session_state.health_data.copy()

df = add_age_group(df)

# 제목
st.title("📊 건강 데이터 분석")
st.caption("연령별 · 성별 건강 지표 분석")

st.markdown("---")

# 필터
st.subheader("분석 조건 선택")

col1, col2 = st.columns(2)

with col1:
    gender = st.multiselect(
        "성별 선택",
        options=["남성", "여성"],
        default=["남성", "여성"]
    )

with col2:
    age_order = [
        "20대 이하",
        "30대",
        "40대",
        "50대",
        "60대",
        "70대 이상"
    ]

    ages = st.multiselect(
        "연령대 선택",
        options=age_order,
        default=age_order
    )

filtered = df[
    df["성별"].isin(gender) &
    df["연령대"].isin(ages)
]

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# 주요 통계
st.markdown("---")
st.subheader("📌 주요 건강 통계")

c1, c2, c3 = st.columns(3)

c1.metric(
    "분석 대상",
    f"{len(filtered):,}명"
)

c2.metric(
    "평균 BMI",
    f"{filtered['BMI'].mean():.2f}"
)

c3.metric(
    "평균 공복혈당",
    f"{filtered['공복혈당'].mean():.2f}"
)

# 건강 지표 선택
st.markdown("---")
st.subheader("📈 연령대별 건강 지표 비교")

selected_metric = st.selectbox(
    "분석할 지표",
    [
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]
)

fig = px.box(
    filtered,
    x="연령대",
    y=selected_metric,
    color="성별",
    points="outliers",
    category_orders={"연령대": age_order},
    title=f"연령대별 {selected_metric} 분포"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 성별 비교
st.markdown("---")
st.subheader("👥 성별 평균 건강 지표 비교")

gender_result = (
    filtered.groupby("성별")[
        ["BMI", "수축기혈압", "이완기혈압", "공복혈당"]
    ]
    .mean()
    .round(2)
    .reset_index()
)

fig = px.bar(
    gender_result.melt(
        id_vars="성별",
        var_name="건강 지표",
        value_name="평균"
    ),
    x="건강 지표",
    y="평균",
    color="성별",
    barmode="group",
    title="성별 건강 지표 평균 비교"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 기술통계
st.markdown("---")
st.subheader("📋 상세 기술통계")

st.dataframe(
    filtered[
        ["BMI", "수축기혈압", "이완기혈압", "공복혈당"]
    ].describe().T.round(2),
    use_container_width=True
)
