
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data import generate_health_data
from utils.analysis import (
    descriptive_statistics,
    correlation_analysis,
    independent_t_test,
    regression_analysis
)


# 페이지 설정
st.set_page_config(
    page_title="통계 분석",
    page_icon="📈",
    layout="wide"
)

# 데이터 불러오기
if "health_data" not in st.session_state:
    st.session_state.health_data = generate_health_data(1000)

df = st.session_state.health_data.copy()

# 제목
st.title("📈 통계 분석 센터")
st.caption("기술통계 · 상관관계 · 가설검정 · 회귀분석")

st.info(
    "가상 건강 데이터를 이용한 교육용 통계 분석입니다."
)

metrics = [
    "BMI",
    "수축기혈압",
    "이완기혈압",
    "공복혈당"
]

# 1. 기술통계
st.header("1. 기술통계 분석")

st.write(
    "평균, 중앙값, 표준편차 등을 통해 데이터의 특징을 확인합니다."
)

desc = descriptive_statistics(df)

st.dataframe(
    desc.round(2),
    use_container_width=True
)

# 2. 상관관계 분석
st.markdown("---")
st.header("2. 상관관계 분석")

corr = correlation_analysis(df)

fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="건강 지표 간 상관관계 히트맵"
)

st.plotly_chart(
    fig_corr,
    use_container_width=True
)

st.caption(
    "상관계수는 -1부터 1까지이며, "
    "인과관계를 직접 증명하지는 않습니다."
)

# 3. 성별 평균 차이 검정
st.markdown("---")
st.header("3. 독립표본 t검정")

selected_metric = st.selectbox(
    "비교할 건강 지표",
    metrics
)

try:
    result = independent_t_test(
        df,
        selected_metric
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "남성 평균",
        f"{result['남성 평균']:.2f}"
    )

    c2.metric(
        "여성 평균",
        f"{result['여성 평균']:.2f}"
    )

    c3.metric(
        "p-value",
        f"{result['p-value']:.4f}"
    )

    if result["p-value"] < 0.05:
        st.success(
            "유의수준 0.05에서 두 집단의 평균 차이가 통계적으로 유의합니다."
        )
    else:
        st.info(
            "유의수준 0.05에서 통계적으로 유의한 평균 차이를 확인하지 못했습니다."
        )

except ValueError as e:
    st.warning(str(e))

# 4. 회귀분석
st.markdown("---")
st.header("4. 다중 선형 회귀분석")

target = st.selectbox(
    "종속변수 선택",
    metrics,
    index=0
)

features = st.multiselect(
    "독립변수 선택",
    [
        col for col in metrics
        if col != target
    ],
    default=[
        col for col in metrics
        if col != target
    ][:2]
)

if st.button("회귀분석 실행"):

    if not features:
        st.warning("독립변수를 선택해 주세요.")

    else:
        try:
            model = regression_analysis(
                df,
                target,
                features
            )

            st.subheader("회귀분석 결과")

            c1, c2 = st.columns(2)

            c1.metric(
                "결정계수 R²",
                f"{model.rsquared:.4f}"
            )

            c2.metric(
                "보정 결정계수",
                f"{model.rsquared_adj:.4f}"
            )

            st.write("회귀계수")

            coef_df = pd.DataFrame({
                "변수": model.params.index,
                "회귀계수": model.params.values,
                "p-value": model.pvalues.values
            })

            st.dataframe(
                coef_df.round(4),
                use_container_width=True
            )

            with st.expander("상세 회귀분석 결과"):
                st.text(model.summary())

        except Exception as e:
            st.error(f"분석 오류: {e}")

# 5. 결과 해석 안내
st.markdown("---")
st.header("5. 통계 분석 해석")

st.markdown(
    """
    - **평균:** 데이터의 전반적인 중심 수준을 나타냅니다.
    - **표준편차:** 데이터가 평균에서 얼마나 퍼져 있는지 나타냅니다.
    - **상관계수:** 두 변수 사이의 선형적인 관계를 나타냅니다.
    - **p-value:** 귀무가설을 가정했을 때 관측된 결과 이상으로 극단적인 결과가 나올 확률입니다.
    - **R²:** 회귀모형이 종속변수의 변동을 얼마나 설명하는지 나타냅니다.

    통계적 유의성이 곧 실제적인 중요성이나 인과관계를 의미하지는 않습니다.
    """
)

