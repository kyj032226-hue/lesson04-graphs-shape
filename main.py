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

# -------------------------------------------------------------------
# 섹션 3: 총 관객 수 분포 (히스토그램)
# -------------------------------------------------------------------
st.header("3. 총 관객 수 분포")

# Plotly 히스토그램 생성
fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="총 관객 수 분포 (히스토그램)",
    labels={"total_audi": "총 관객 수 (명)", "count": "영화 수"},
    hover_data=["movieNm"],
)

fig3.update_traces(
    hovertemplate="<b>관객 수 구간</b>: %{x}<br><b>영화 수</b>: %{y}편"
)

st.plotly_chart(fig3, use_container_width=True)

# 주요 데이터 계산 (가장 관객 수가 많은 영화)
max_movie = df.loc[df["total_audi"].idxmax()]
max_title = max_movie["movieNm"]
max_audi = max_movie["total_audi"]

# 그래프 분석 내용 안내 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 **하위 관객 수 구간(100만~300만 명 대)**에 밀집되어 있으며, "
    f"가장 많은 관객을 동원한 영화는 **'{max_title}'** (총 {max_audi:,}명)입니다."
)

st.divider()

# -------------------------------------------------------------------
# 섹션 4: 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
# -------------------------------------------------------------------
st.header("4. 개봉일 스크린 수 vs 총 관객 수")

# Plotly 산점도 생성
fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="main_genre",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객 수의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수 (개)",
        "total_audi": "총 관객 수 (명)",
        "main_genre": "장르",
    },
    hover_data={"first_scrn": ":,d", "total_audi": ":,d"},
)

# 마우스 오버 시 표시되는 툴팁 설정
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명"
)

st.plotly_chart(fig4, use_container_width=True)

# 그래프 분석 내용 안내 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린 수가 많을수록 대체로 총 관객 수가 증가하는 양의 상관관계를 보이지만, 스크린 수 대비 상대적으로 높은 흥행 실적을 거둔 장르별 대표작들도 함께 파악할 수 있습니다."
)

st.divider()
