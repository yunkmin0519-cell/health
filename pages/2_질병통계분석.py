
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data import generate_health_data, add_age_group


# 페이지 설정
st.set_page_config(
    page_title="질병 통계 분석",
    page_icon="🩺",
    layout="wide"
)

# 데이터 불러오기
if "health_data" not in st.session_state:
    st.session_state.health_data = generate_health_data(1000)

df = st.session_state.health_data.copy()
df = add_age_group(df)

# 제목
st.title("🩺 건강 위험 지표 분석")
st.caption("건강 지표의 분포와 연령대별 통계 분석")

st.info(
    "이 페이지는 교육 및 통계 분석을 위한 자료입니다. "
    "실제 질병 진단이나 유병률을 나타내지 않습니다."
)

st.markdown("---")

# 분석 지표 선택
st.subheader("1. 분석 지표 선택")

metric = st.selectbox(
    "분석할 건강 지표",
    ["공복혈당", "수축기혈압", "이완기혈압", "BMI"]
)

thresholds = {
    "공복혈당": 126,
    "수축기혈압": 140,
    "이완기혈압": 90,
    "BMI": 25
}

threshold = thresholds[metric]

# 기준별 분류
df["분류"] = df[metric].apply(
    lambda x: "기준 이상" if x >= threshold else "기준 미만"
)

# 주요 통계
st.markdown("---")
st.subheader("2. 주요 분석 결과")

total = len(df)
above = (df["분류"] == "기준 이상").sum()

ratio = above / total * 100 if total > 0 else 0

c1, c2, c3 = st.columns(3)

c1.metric("전체 분석 대상", f"{total:,}명")
c2.metric("기준 이상 관측 수", f"{above:,}명")
c3.metric("기준 이상 비율", f"{ratio:.1f}%")

# 기준별 비율 그래프
st.markdown("---")
st.subheader("3. 기준별 관측 비율")

count_df = (
    df["분류"]
    .value_counts()
    .rename_axis("분류")
    .reset_index(name="인원")
)

fig = px.pie(
    count_df,
    names="분류",
    values="인원",
    hole=0.45,
    color_discrete_sequence=["#2563EB", "#F97316"],
    title=f"{metric} 기준별 비율"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 연령대별 기준 이상 비율
st.markdown("---")
st.subheader("4. 연령대별 기준 이상 비율")

age_result = (
    df.groupby("연령대", observed=True)["분류"]
    .apply(lambda x: (x == "기준 이상").mean() * 100)
    .reset_index(name="비율")
)

fig = px.bar(
    age_result,
    x="연령대",
    y="비율",
    color="비율",
    text_auto=".1f",
    color_continuous_scale="Oranges",
    title=f"연령대별 {metric} 기준 이상 비율"
)

fig.update_layout(
    template="plotly_white",
    yaxis_title="비율(%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 지표 분포
st.markdown("---")
st.subheader("5. 건강 지표 분포")

fig = px.histogram(
    df,
    x=metric,
    color="분류",
    marginal="box",
    barmode="overlay",
    opacity=0.75,
    title=f"{metric} 분포 분석"
)

fig.add_vline(
    x=threshold,
    line_dash="dash",
    line_color="red",
    annotation_text="분석 기준"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 상세 통계
st.markdown("---")
st.subheader("6. 연령대별 상세 통계")

summary = (
    df.groupby("연령대", observed=True)
    .agg(
        분석인원=("연령", "count"),
        평균수치=(metric, "mean"),
        기준이상인원=(
            "분류",
            lambda x: (x == "기준 이상").sum()
        )
    )
    .round(2)
)

summary["기준이상비율(%)"] = (
    summary["기준이상인원"] /
    summary["분석인원"] * 100
).round(2)

st.dataframe(
    summary,
    use_container_width=True
)

# CSV 다운로드
st.download_button(
    "📥 분석 결과 다운로드",
    data=summary.to_csv(encoding="utf-8-sig"),
    file_name="disease_statistics.csv",
    mime="text/csv"
)

