import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사용자 정의 커스텀 CSS (깔끔한 다크/라이트 모드 통합 스타일링)
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    .metric-card {
        background-color: rgba(120, 120, 120, 0.08);
        border-radius: 12px;
        padding: 16px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #888888;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
    }
    .insight-box {
        background-color: rgba(28, 131, 225, 0.08);
        border-radius: 8px;
        padding: 14px 18px;
        border-left: 4px solid #1C83E1;
        margin-top: 12px;
        margin-bottom: 18px;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    """KOBIS 박스오피스 데이터를 불러오고 필드를 정제합니다."""
    try:
        df = pd.read_csv(DATA_URL)
        
        # 컬럼명 매핑 (한글/영문 모두 대응)
        col_map = {
            'movieNm': '영화명',
            'openDt': '개봉일',
            'salesAcc': '매출액',
            'audiAcc': '관객수',
            'scrnCnt': '스크린수',
            'showCnt': '상영횟수',
            'repGenreNm': '장르',
            'genre': '장르',
            'repNationNm': '국적',
            'nation': '국적'
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        
        # 숫자형 데이터 변환 및 결측치 처리
        numeric_cols = ['매출액', '관객수', '스크린수', '상영횟수']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        if '장르' in df.columns:
            df['장르'] = df['장르'].fillna('기타').replace('', '기타')
        else:
            df['장르'] = '기타'
            
        if '영화명' not in df.columns:
            df['영화명'] = '미상'
            
        # 관객수가 0명 초과인 데이터만 유지
        df = df[df['관객수'] > 0].copy()
        
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        # 오류 발생 시 더미 데이터 생성
        dummy_data = {
            '영화명': ['명량', '극한직업', '신과함께-죄와 벌', '국제시장', '베테랑', '괴물', '도둑들', '7번방의 선물'],
            '장르': ['액션', '코미디', '판타지', '드라마', '액션', 'SF', '범죄', '코미디'],
            '관객수': [17615844, 16264944, 14411675, 14257114, 13414211, 10917221, 12983841, 12811206],
            '매출액': [135748398910, 139651845516, 115698654137, 110828000000, 105168000000, 80000000000, 93600000000, 91400000000]
        }
        return pd.DataFrame(dummy_data)

df = load_data()

st.sidebar.title("🎛️ 데이터 필터 설정")

# 장르 선택
all_genres = sorted(df['장르'].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "표시할 장르 선택",
    options=all_genres,
    default=all_genres[:8] if len(all_genres) >= 8 else all_genres
)

# 최소 관객수 필터
min_audi = st.sidebar.slider(
    "최소 관객수 필터 (명)",
    min_value=0,
    max_value=int(df['관객수'].max()),
    value=10000,
    step=10000,
    format="%d"
)

# 상위 영화 개수 제한
top_n = st.sidebar.number_input("장르당 상위 영화 표시 수 Limit", min_value=1, max_value=100, value=15)

# 필터링 적용
filtered_df = df[
    (df['장르'].isin(selected_genres)) & 
    (df['관객수'] >= min_audi)
].copy()

# 장르별 상위 N개 추출
filtered_df = filtered_df.groupby('장르').apply(
    lambda x: x.nlargest(top_n, '관객수')
).reset_index(drop=True)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("박스오피스 데이터를 바탕으로 장르별 영화 관객수 분포와 위계구조를 시각화합니다.")

# 메트릭 카드 영역
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">분석 대상 영화 수</div>
            <div class="metric-value">{len(filtered_df):,}개</div>
        </div>
    """, unsafe_unsafe_html=True if hasattr(st, 'unsafe_html') else True, unsafe_html=True)
with m2:
    total_audi_sum = filtered_df['관객수'].sum()
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">총 관객수 합계</div>
            <div class="metric-value">{total_audi_sum/10000:,.0f}만 명</div>
        </div>
    """, unsafe_unsafe_html=True if hasattr(st, 'unsafe_html') else True, unsafe_html=True)
with m3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">선택된 장르 수</div>
            <div class="metric-value">{filtered_df['장르'].nunique()}개</div>
        </div>
    """, unsafe_unsafe_html=True if hasattr(st, 'unsafe_html') else True, unsafe_html=True)
with m4:
    top_movie = filtered_df.loc[filtered_df['관객수'].idxmax()]['영화명'] if not filtered_df.empty else "-"
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">최다 관객 영화</div>
            <div class="metric-value" style="font-size: 1.2rem; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{top_movie}</div>
        </div>
    """, unsafe_unsafe_html=True if hasattr(st, 'unsafe_html') else True, unsafe_html=True)

st.divider()

st.subheader("1️⃣ 장르별 관객수 요약")

genre_summary = filtered_df.groupby('장르')['관객수'].agg(['sum', 'count']).reset_index()
genre_summary.columns = ['장르', '총관객수', '영화수']
genre_summary = genre_summary.sort_values(by='총관객수', ascending=False)

fig1 = px.bar(
    genre_summary,
    x='장르',
    y='총관객수',
    text_auto='.2s',
    color='총관객수',
    color_continuous_scale='Reds',
    title="장르별 총 관객수 비교"
)
fig1.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수 (명)",
    height=380,
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

st.subheader("2️⃣ 장르 & 영화 관객수 트리맵 (Treemap)")

if filtered_df.empty:
    st.warning("선택된 필터 조건에 해당하는 영화 데이터가 없습니다. 사이드바 조건을 변경해 주세요.")
else:
    # 트리맵 생성: 장르(상위 계층) -> 영화명(하위 계층)
    # 칸 크기(values): 관객수 (total_audi)
    fig_treemap = px.treemap(
        filtered_df,
        path=[px.Constant("전체 영화"), '장르', '영화명'],
        values='관객수',
        color='장르',
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="장르 및 영화별 관객수 점유율 트리맵"
    )

    # 마우스 오버(Hover) 툴팁 커스터마이징
    fig_treemap.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,.0f}명<extra></extra>",
        textinfo="label+value"
    )

    fig_treemap.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

    # 데이터 인사이트 영역
    st.markdown("""
        <div class="insight-box">
            💡 <b>트리맵 활용 안내:</b><br>
            • Each block area corresponds directly to the total audience count (<code>total_audi</code>) of each movie.<br>
            • 마우스를 각 사각형 영역 위에 올리면 해당 <b>영화명</b>과 <b>총 관객수</b>를 확인하실 수 있습니다.<br>
            • 상위 계층(장르)을 클릭하면 해당 장르 세부 영역으로 확대(Zoom-in)되어 더욱 명확하게 비교할 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

with st.expander("📄 데이터 상세보기"):
    st.dataframe(
        filtered_df[['장르', '영화명', '관객수', '매출액']].sort_values(by='관객수', ascending=False),
        use_container_width=True,
        column_config={
            "관객수": st.column_config.NumberColumn(format="%d 명"),
            "매출액": st.column_config.NumberColumn(format="%d 원")
        }
    )
