
import numpy as np
import pandas as pd


# 필요한 데이터 컬럼
REQUIRED_COLUMNS = [
    "연령",
    "성별",
    "키",
    "체중",
    "BMI",
    "수축기혈압",
    "이완기혈압",
    "공복혈당"
]


def generate_health_data(n=1000, seed=42):
    """
    가상의 건강 데이터 생성 함수
    n: 생성할 데이터 수
    seed: 동일한 결과를 위한 난수 설정
    """

    rng = np.random.default_rng(seed)

    # 기본 정보
    age = rng.integers(20, 80, n)

    gender = rng.choice(
        ["남성", "여성"],
        size=n
    )

    # 키와 체중
    height = np.where(
        gender == "남성",
        rng.normal(172, 6, n),
        rng.normal(160, 5.5, n)
    )

    weight = rng.normal(
        65 + (age - 40) * 0.12,
        10,
        n
    )

    # BMI 계산
    bmi = weight / ((height / 100) ** 2)

    # 혈압 생성
    systolic = (
        105
        + age * 0.28
        + (bmi - 22) * 1.1
        + rng.normal(0, 10, n)
    )

    diastolic = (
        65
        + age * 0.12
        + (bmi - 22) * 0.5
        + rng.normal(0, 7, n)
    )

    # 공복혈당 생성
    glucose = (
        82
        + age * 0.25
        + (bmi - 22) * 1.1
        + rng.normal(0, 13, n)
    )

    # 생활습관
    exercise = rng.integers(0, 8, n)

    smoking = rng.choice(
        ["흡연", "비흡연"],
        size=n,
        p=[0.3, 0.7]
    )

    # 데이터프레임 생성
    df = pd.DataFrame({
        "연령": age,
        "성별": gender,
        "키": np.round(height, 1),
        "체중": np.round(weight, 1),
        "BMI": np.round(bmi, 1),
        "수축기혈압": np.round(systolic, 1),
        "이완기혈압": np.round(diastolic, 1),
        "공복혈당": np.round(glucose, 1),
        "주당운동횟수": exercise,
        "흡연여부": smoking
    })

    return df


def validate_data(df):
    """데이터의 필수 컬럼과 형식 검사"""

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        return False, (
            f"필수 컬럼이 없습니다: {', '.join(missing)}"
        )

    if df.empty:
        return False, "데이터가 비어 있습니다."

    if not df["성별"].isin(["남성", "여성"]).all():
        return False, "성별은 남성 또는 여성이어야 합니다."

    return True, "데이터 확인 완료"


def load_uploaded_data(file):
    """CSV 파일 업로드 및 전처리"""

    df = pd.read_csv(
        file,
        encoding="utf-8-sig"
    )

    valid, message = validate_data(df)

    if not valid:
        raise ValueError(message)

    numeric_cols = [
        "연령",
        "키",
        "체중",
        "BMI",
        "수축기혈압",
        "이완기혈압",
        "공복혈당"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=numeric_cols
    )

    if df.empty:
        raise ValueError(
            "유효한 숫자 데이터가 없습니다."
        )

    if (df[numeric_cols] <= 0).any().any():
        raise ValueError(
            "건강 지표에는 0 이하의 값이 포함될 수 없습니다."
        )

    return df


def add_age_group(df):
    """연령을 연령대별로 구분"""

    result = df.copy()

    result["연령대"] = pd.cut(
        result["연령"],
        bins=[0, 29, 39, 49, 59, 69, 120],
        labels=[
            "20대 이하",
            "30대",
            "40대",
            "50대",
            "60대",
            "70대 이상"
        ]
    )

    return result
