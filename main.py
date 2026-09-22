import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")


# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 장르 전처리: 세로막대 기호(|)로 분리된 경우 첫 번째 장르만 추출
    df["main_genre"] = df["genre"].astype(str).apply(lambda x: x.split("|")[0])

    return df


df = load_data()

# -------------------------------------------------------------------
# 섹션 1: 장르별 영화 편수 (도넛 차트)
# -------------------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df["main_genre"].value_counts().reset_index()
genre_counts.columns = ["장르", "편수"]

# Plotly 도넛 차트 생성
fig1 = px.pie(
    genre_counts,
    values="편수",
    names="장르",
    hole=0.4,
    title="장르별 영화 편수 비율",
)

# 마우스 오버 시 편수와 비율이 함께 표시되도록 설정
fig1.update_traces(
    hovertemplate="<b>장르</b>: %{label}<br><b>편수</b>: %{value}편<br><b>비율</b>: %{percent}"
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 분석 내용 안내 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "박스오피스 상위권 영화 중 특정 주요 장르가 차지하는 비중과 개별 장르의 분포를 한눈에 비교할 수 있습니다."
)

st.divider()

# -------------------------------------------------------------------
# 섹션 2: 장르 및 영화별 총 관객 수 (트리맵)
# -------------------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객 수 트리맵")

# Plotly 트리맵 차트 생성
fig2 = px.treemap(
    df,
    path=[px.Constant("전체 영화"), "main_genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 구조",
    hover_data={"movieNm": True, "total_audi": ":,d"},
)

# 마우스 오버 시 정보 커스텀 설정
fig2.update_traces(hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명")

st.plotly_chart(fig2, use_container_width=True)

# 그래프 분석 내용 안내 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "장르별 전체 관객 규모의 크기 비교뿐만 아니라, 특정 장르 흥행을 견인한 대표 영화와 그 관객 수 비중을 구체적으로 확인할 수 있습니다."
)

st.divider()
