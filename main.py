import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .insight-box {
        background-color: #F0FDF4;
        border-left: 5px solid #22C55E;
        padding: 12px 18px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 25px;
        font-size: 0.98rem;
        color: #166534;
    }
    .insight-title {
        font-weight: bold;
        color: #15803D;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_movie_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    try:
        df = pd.read_csv(url)
        
        # 장르 세로막대(|) 기준 첫 번째 장르만 추출
        if 'genre' in df.columns:
            df['genre_clean'] = df['genre'].fillna('기타').astype(str).apply(
                lambda x: x.split('|')[0].strip() if x.strip() != '' else '기타'
            )
        else:
            df['genre_clean'] = '기타'
            
        # 수치형 컬럼 변환
        num_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        # 개봉일 날짜형 변환
        if 'openDt' in df.columns:
            df['openDt_formatted'] = pd.to_datetime(
                df['openDt'].astype(str), format='%Y%m%d', errors='coerce'
            ).dt.strftime('%Y-%m-%d')
        
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df_raw = load_movie_data()

st.markdown('<div class="main-header">🎬 영화 데이터 그래프 도감 2 - 분포와 관계</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">박스오피스 Top 10 진입 216편 영화의 장르 분포 및 주요 흥행 지표 간 관계 분석</div>', unsafe_allow_html=True)

if df_raw.empty:
    st.warning("데이터를 불러올 수 없습니다. 인터넷 연결 상태를 확인해 주세요.")
    st.stop()

st.sidebar.header("🔍 데이터 필터링")

# 장르 선택 필터
all_genres = sorted(df_raw['genre_clean'].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "장르 선택",
    options=all_genres,
    default=all_genres,
    help="분석에 포함할 영화 장르를 선택하세요."
)

# 제작 국가 선택 필터
all_nations = sorted(df_raw['nation'].dropna().unique().tolist())
selected_nations = st.sidebar.multiselect(
    "제작 국가 선택",
    options=all_nations,
    default=all_nations,
    help="분석에 포함할 제작 국가를 선택하세요."
)

# 총 관객수 범위 필터
min_audi = int(df_raw['total_audi'].min())
max_audi = int(df_raw['total_audi'].max())
selected_audi_range = st.sidebar.slider(
    "총 관객수 범위 (명)",
    min_value=min_audi,
    max_value=max_audi,
    value=(min_audi, max_audi),
    step=100000,
    format="%d"
)

df_filtered = df_raw[
    (df_raw['genre_clean'].isin(selected_genres)) &
    (df_raw['nation'].isin(selected_nations)) &
    (df_raw['total_audi'] >= selected_audi_range[0]) &
    (df_raw['total_audi'] <= selected_audi_range[1])
]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("분석 대상 영화 수", f"{len(df_filtered):,} 편")
with m2:
    st.metric("총 관객 수 합계", f"{df_filtered['total_audi'].sum():,/d} 명")
with m3:
    st.metric("평균 스크린 수 (개봉일)", f"{int(df_filtered['first_scrn'].mean()):,} 개")
with m4:
    st.metric("평균 Top10 유지 기간", f"{df_filtered['days_in_top10'].mean():.1f} 일")

st.divider()

tab1, tab2, tab3 = st.tabs(["🍩 1. 장르 및 수치 분포", "📈 2. 흥행 지표 간 관계", "📊 3. 상관관계 & 데이터 도감"])

with tab1:
    st.subheader("1-1. 장르별 영화 편수 비율 (도넛 그래프)")
    
    # 장르별 집계 데이터 생성
    genre_counts = df_filtered['genre_clean'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']
    
    # 플롯리 도넛 그래프 작성 (Hover시 편수와 비율 표출)
    fig_donut = px.pie(
        genre_counts,
        names='장르',
        values='편수',
        hole=0.45,
        title="장르별 영화 편수 구성비",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_donut.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )
    fig_donut.update_layout(
        font=dict(family="Inter, sans-serif", size=13),
        legend_title_text="장르 목록",
        margin=dict(t=50, b=20, l=20, r=20),
        height=480
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # 인사이트 전달 영역
    st.markdown("""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            국내 박스오피스 상위권 영화 중 특정 주요 장르(드라마, 액션, 애니메이션 등)가 전체 편수의 과반수 이상을 차지하며 높은 비중을 형성하고 있음을 확인할 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("1-2. 흥행 지표별 데이터 분포 탐색 (히스토그램 & 박스플롯)")
    
    metric_choice = st.selectbox(
        "분석할 지표를 선택하세요:",
        options=[
            ('total_audi', '총 관객수 (명)'),
            ('first_week_audi', '개봉 첫 주 관객수 (명)'),
            ('first_scrn', '개봉일 스크린수 (개)'),
            ('first_show', '개봉일 상영횟수 (회)'),
            ('days_in_top10', '10위권 머문 날수 (일)')
        ],
        format_func=lambda x: x[1]
    )
    
    col_code, col_name = metric_choice
    
    fig_hist = px.histogram(
        df_filtered,
        x=col_code,
        color='genre_clean',
        marginal="box",
        title=f"{col_name} 분포 현황",
        labels={col_code: col_name, 'genre_clean': '장르'},
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_hist.update_layout(
        xaxis_title=col_name,
        yaxis_title="영화 수",
        height=450,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            선택한 <b>{col_name}</b> 지표는 대다수의 영화가 하위 구간에 밀집되어 있는 반면, 일부 초대형 흥행작만이 오른쪽 긴 꼬리(Right-skewed) 형태의 극단적 상위 수치를 기록하는 전형적인 롱테일 분포를 보여줍니다.
        </div>
    """, unsafe_allow_html=True)


with tab2:
    st.subheader("2-1. 개봉일 스크린 수 vs 총 관객 수 (버블 차트)")
    
    fig_scatter1 = px.scatter(
        df_filtered,
        x='first_scrn',
        y='total_audi',
        size='days_in_top10',
        color='genre_clean',
        hover_name='movieNm',
        hover_data={'openDt_formatted': True, 'first_week_audi': ':,', 'total_audi': ':,', 'days_in_top10': True},
        title="개봉일 스크린 수가 총 관객 수에 미치는 영향 (버블 크기: Top10 유지일수)",
        labels={
            'first_scrn': '개봉일 스크린 수 (개)',
            'total_audi': '총 관객 수 (명)',
            'genre_clean': '장르',
            'days_in_top10': 'Top10 유지일수',
            'openDt_formatted': '개봉일'
        },
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_scatter1.update_layout(height=500, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_scatter1, use_container_width=True)
    
    st.markdown("""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            개봉일 스크린 수가 확보될수록 초기 관객 동원이 용이해지며, 여기에 Top 10 유지 기간(버블 크기)이 길어질수록 최종 총 관객 수가 시너지 효과를 내며 폭발적으로 증가하는 상호관계를 보입니다.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("2-2. 개봉 첫 주 관객 수 vs 최종 총 관객 수 (회귀 추세선)")
    
    fig_scatter2 = px.scatter(
        df_filtered,
        x='first_week_audi',
        y='total_audi',
        color='genre_clean',
        trendline="ols",
        hover_name='movieNm',
        title="개봉 첫 주 성적과 최종 성적 간의 선형 관계",
        labels={
            'first_week_audi': '개봉 첫 주 관객 수 (명)',
            'total_audi': '최종 총 관객 수 (명)',
            'genre_clean': '장르'
        }
    )
    fig_scatter2.update_layout(height=500, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_scatter2, use_container_width=True)
    
    st.markdown("""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            개봉 첫 주 관객 수와 최종 관객 수는 강한 양의 선형 관계를 가지므로, 개봉 1주일 간의 흥행 실적이 최종 흥행 성공 여부를 예측하는 매우 강력한 결정 요인임을 알 수 있습니다.
        </div>
    """, unsafe_allow_html=True)


with tab3:
    st.subheader("3-1. 주요 수치형 변수 간 상관관계 (Correlation Matrix)")
    
    corr_cols = {
        'first_scrn': '개봉일 스크린수',
        'first_show': '개봉일 상영횟수',
        'first_week_audi': '첫주 관객수',
        'total_audi': '총 관객수',
        'days_in_top10': 'Top10 유지일수'
    }
    
    corr_df = df_filtered[list(corr_cols.keys())].rename(columns=corr_cols).corr()
    
    fig_heatmap = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Reds",
        title="흥행 주요 지표 간 상관계수 히트맵"
    )
    fig_heatmap.update_layout(height=420, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            개봉일 스크린수와 개봉일 상영횟수 간에는 매우 높은 상관관계가 존재하며, 스크린 수보다 개봉 첫 주 관객수가 최종 관객수와 더욱 높은 상관관계를 형성함을 알 수 있습니다.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("3-2. 원본 데이터 상세 조회 도감")
    
    # 테이블 표시용 컬럼 정리
    display_df = df_filtered[[
        'movieNm', 'genre_clean', 'nation', 'openDt_formatted', 
        'first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10'
    ]].copy()
    
    display_df.columns = [
        '영화명', '장르', '제작국가', '개봉일', 
        '개봉일 스크린수', '개봉일 상영횟수', '개봉 첫주 관객수', '총 관객수', 'Top10 유지일수'
    ]
    
    st.dataframe(
        display_df.sort_values(by='총 관객수', ascending=False),
        use_container_width=True,
        hide_index=True
    )
