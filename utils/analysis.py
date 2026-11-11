
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm


# 1. 기술통계 분석
def descriptive_statistics(df):
    """
    건강 데이터의 평균, 중앙값, 표준편차 등을 계산한다.
    """

    columns = [
        "연령",
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]

    # 데이터에 존재하는 컬럼만 선택
    available = [col for col in columns if col in df.columns]

    if not available:
        raise ValueError("분석할 수 있는 건강 지표가 없습니다.")

    return df[available].describe().T


# 2. 상관관계 분석
def correlation_analysis(df):
    """
    건강 지표 사이의 피어슨 상관계수를 계산한다.
    """

    columns = [
        "연령",
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]

    available = [col for col in columns if col in df.columns]

    if len(available) < 2:
        raise ValueError("상관관계 분석에는 숫자형 변수가 2개 이상 필요합니다.")

    return df[available].corr(method="pearson")


# 3. 독립표본 t검정
def independent_t_test(df, column):
    """
    남성과 여성의 평균 차이를 Welch t검정으로 분석한다.
    """

    if "성별" not in df.columns or column not in df.columns:
        raise ValueError("필요한 데이터 컬럼이 없습니다.")

    male = pd.to_numeric(
        df.loc[df["성별"] == "남성", column],
        errors="coerce"
    ).dropna()

    female = pd.to_numeric(
        df.loc[df["성별"] == "여성", column],
        errors="coerce"
    ).dropna()

    if len(male) < 2 or len(female) < 2:
        raise ValueError("각 집단에 최소 2개 이상의 데이터가 필요합니다.")

    result = stats.ttest_ind(
        male,
        female,
        equal_var=False
    )

    return {
        "남성 평균": male.mean(),
        "여성 평균": female.mean(),
        "t 통계량": result.statistic,
        "p-value": result.pvalue
    }


# 4. 다중 선형 회귀분석
def regression_analysis(df, target, features):
    """
    여러 독립변수를 활용하여 종속변수를 설명하는 회귀모형을 만든다.
    """

    if not features:
        raise ValueError("독립변수를 하나 이상 선택해야 합니다.")

    if target in features:
        raise ValueError("종속변수와 독립변수는 서로 달라야 합니다.")

    required = [target] + features

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"존재하지 않는 컬럼: {missing}")

    data = df[required].apply(
        pd.to_numeric,
        errors="coerce"
    ).dropna()

    if len(data) <= len(features) + 2:
        raise ValueError("회귀분석에 필요한 데이터가 부족합니다.")

    X = data[features]
    y = data[target]

    # 상수항 추가
    X = sm.add_constant(X)

    # 회귀모형 생성
    model = sm.OLS(y, X).fit()

    return model


# 5. BMI 분류
def bmi_classification(bmi):
    """
    BMI 수치를 기준으로 분석용 분류를 반환한다.
    """

    if pd.isna(bmi) or bmi <= 0:
        return "잘못된 값"

    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "비만 전 단계"
    elif bmi < 30:
        return "비만"
    else:
        return "고도비만"


# 6. 분석 결과 요약
def get_health_summary(df):
    """
    주요 건강 지표의 평균을 계산한다.
    """

    columns = [
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]

    available = [col for col in columns if col in df.columns]

    if not available:
        raise ValueError("요약할 건강 데이터가 없습니다.")

    return df[available].mean().round(2)
