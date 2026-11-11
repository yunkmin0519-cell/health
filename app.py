
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data import (
    generate_health_data,
    load_uploaded_data,
    add_age_group
)

from utils.analysis import get_health_summary


# --------------------------------
# 1. 페이지 기본 설정
# --------------------------------

st.set_page_config(
    page_title="HEALTH INSIGHT",
    page_icon="🏥",
    layout="wide"
)


# --------------------------------
# 2. 데이터 초기화
# --------------------------------

if "health_data" not in st.session_state:
    st.session_state.health_data = generate_health_data(1000)

df = st.session_state.health_data.copy()


# --------------------------------
# 3. 사이드바
# --------------------------------

st.sidebar.title("🏥 HEALTH INSIGHT")
st.sidebar.caption("Healthcare Statistics Dashboard")

st.sidebar.markdown("---")

st.sidebar.subheader("데이터 관리")

uploaded_file = st.sidebar.file_uploader(
    "건강 데이터 CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        new_df = load_uploaded_data(uploaded_file)
        st.session_state.health_data = new_df
        st.sidebar.success("데이터 업로드 완료")
        df = new_df.copy()

    except Exception as e:
        st.sidebar.error(f"업로드 오류: {e}")

if st.sidebar.button("가상 데이터로 초기화"):
    st.session_state.health_data = generate_health_data(1000)
    st.rerun()


# --------------------------------
# 4. 데이터 전처리
# --------------------------------

df = add_age_group(df)


# --------------------------------
# 5. 메인 화면
# --------------------------------

st.title("🏥 HEALTH INSIGHT")

st.markdown(
    """
    ### Healthcare & Medical Statistics Dashboard

    건강 데이터를 수집하고 분석하여
    다양한 건강 지표의 통계적 특징을 확인하는 웹 대시보드입니다.
    """
)

st.info(
    "현재 가상 데이터가 사용되고 있습니다. "
    "실제 의료 진단이나 건강 상태를 나타내는 자료가 아닙니다."
)


# --------------------------------
# 6. 주요 건강 지표
# --------------------------------

st.header("📊 주요 건강 통계")

summary = get_health_summary(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "분석 대상",
    f"{len(df):,}명"
)

col2.metric(
    "평균 BMI",
    f"{summary['BMI']:.2f}"
)

col3.metric(
    "평균 수축기혈압",
    f"{summary['수축기혈압']:.1f}"
)

col4.metric(
    "평균 공복혈당",
    f"{summary['공복혈당']:.1f}"
)


st.markdown("---")


# --------------------------------
# 7. 연령대별 인원 분석
# --------------------------------

st.header("👥 연령대별 데이터 분포")

age_data = (
    df["연령대"]
    .value_counts()
    .sort_index()
    .reset_index()
)

age_data.columns = ["연령대", "인원"]

fig_age = px.bar(
    age_data,
    x="연령대",
    y="인원",
    color="인원",
    text="인원",
    color_continuous_scale="Blues",
    title="연령대별 분석 대상 인원"
)

fig_age.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig_age,
    use_container_width=True
)


# --------------------------------
# 8. 성별 BMI 분석
# --------------------------------

st.header("⚖️ 성별 건강 지표 비교")

gender_data = (
    df.groupby("성별")["BMI"]
    .mean()
    .reset_index()
)

fig_gender = px.bar(
    gender_data,
    x="성별",
    y="BMI",
    color="성별",
    text_auto=".2f",
    title="성별 평균 BMI 비교",
    color_discrete_sequence=["#2563EB", "#EC4899"]
)

fig_gender.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig_gender,
    use_container_width=True
)


# --------------------------------
# 9. 건강 지표 분포 분석
# --------------------------------

st.header("📈 건강 지표 분포")

selected_metric = st.selectbox(
    "분석할 건강 지표 선택",
    [
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]
)

fig_hist = px.histogram(
    df,
    x=selected_metric,
    nbins=30,
    marginal="box",
    title=f"{selected_metric} 분포 분석",
    color_discrete_sequence=["#2563EB"]
)

fig_hist.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig_hist,
    use_container_width=True
)


# --------------------------------
# 10. 데이터 미리보기
# --------------------------------

st.header("📋 건강 데이터 미리보기")

st.dataframe(
    df.head(20),
    use_container_width=True,
    hide_index=True
)


# --------------------------------
# 11. 데이터 다운로드
# --------------------------------

csv_data = df.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 데이터 CSV 다운로드",
    data=csv_data,
    file_name="health_insight_data.csv",
    mime="text/csv"
)


# --------------------------------
# 12. 마무리
# --------------------------------

st.markdown("---")

st.caption(
    "HEALTH INSIGHT | Healthcare Data Analytics Project"
)
