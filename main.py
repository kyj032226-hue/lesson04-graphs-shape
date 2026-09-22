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

# Custom CSS for UI embellishments
st.markdown("""
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.8rem;
    }
    .insight-box {
        background-color: #F0F9FF;
        border-left: 5px solid #0284C7;
        padding: 14px 18px;
        border-radius: 8px;
        margin-top: 12px;
        margin-bottom: 28px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .insight-title {
        color: #0369A1;
        font-weight: 700;
        font-size: 1.02rem;
        margin-bottom: 4px;
    }
    .insight-content {
        color: #334155;
        font-size: 0.96rem;
        line-height: 1.5;
    }
    </style>
""", unsafe_allowed_html=True)


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        
        # Preprocessing: Clean genre (extract first genre if split by '|')
        df['genre_original'] = df['genre']
        df['genre'] = df['genre'].astype(str).apply(
            lambda x: x.split('|')[0].strip() if pd.notna(x) and x != 'nan' and x.strip() != '' else '기타'
        )
        
        # Numeric column parsing
        num_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        # Clean country/nation
        df['nation'] = df['nation'].fillna('미상')
        
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df_raw = load_data()


def render_insight_box(insight_text: str):
    """Renders a styled callout section below each graph for takeaways."""
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">💡 이 그래프로 알 수 있는 것</div>
            <div class="insight-content">{insight_text}</div>
        </div>
        """,
        unsafe_allowed_html=True
    )


st.sidebar.header("🔍 데이터 필터링")

if not df_raw.empty:
    # Genre filter
    all_genres = sorted(list(df_raw['genre'].unique()))
    selected_genres = st.sidebar.multiselect(
        "장르 선택",
        options=all_genres,
        default=all_genres,
        help="분석에 포함할 장르를 선택하세요."
    )

    # Nation filter
    all_nations = sorted(list(df_raw['nation'].unique()))
    selected_nations = st.sidebar.multiselect(
        "제작 국가 선택",
        options=all_nations,
        default=all_nations,
        help="분석에 포함할 제작 국가를 선택하세요."
    )

    # Audience range filter
    min_audi = int(df_raw['total_audi'].min())
    max_audi = int(df_raw['total_audi'].max())
    selected_audi_range = st.sidebar.slider(
        "총 관객 수 범위 (명)",
        min_value=min_audi,
        max_value=max_audi,
        value=(min_audi, max_audi),
        step=10000,
        format="%d명"
    )

    # Filter application
    filtered_df = df_raw[
        (df_raw['genre'].isin(selected_genres)) &
        (df_raw['nation'].isin(selected_nations)) &
        (df_raw['total_audi'] >= selected_audi_range[0]) &
        (df_raw['total_audi'] <= selected_audi_range[1])
    ].copy()
else:
    filtered_df = pd.DataFrame()


st.markdown('<div class="main-title">🎬 영화 데이터 그래프 도감 2 - 분포와 관계</div>', unsafe_allowed_html=True)
st.markdown('<div class="sub-title">박스오피스 상위권 영화 216편의 개봉 스크린 수, 관객 수, 장르, TOP10 잔류 일수 간의 분포와 상관관계를 분석합니다.</div>', unsafe_allowed_html=True)

if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 영화 데이터가 없습니다. 필터를 조정해 주세요.")
else:
    # Summary Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("총 분석 영화 수", f"{len(filtered_df):,} 편")
    with m2:
        st.metric("평균 총 관객 수", f"{int(filtered_df['total_audi'].mean()):,} 명")
    with m3:
        top_movie = filtered_df.loc[filtered_df['total_audi'].idxmax()]['movieNm'] if not filtered_df.empty else "-"
        st.metric("최다 관객 영화", top_movie)
    with m4:
        st.metric("평균 개봉일 스크린 수", f"{int(filtered_df['first_scrn'].mean()):,} 개")

    st.markdown("---")


    st.subheader("1. 장르별 영화 편수 분포 (도넛 그래프)")
    
    # Calculate genre counts
    genre_counts = filtered_df['genre'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']

    # Donut Chart
    fig_donut = px.pie(
        genre_counts,
        values='count',
        names='genre',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Custom hover template showing count and percentage
    fig_donut.update_traces(
        textinfo='percent+label',
        hovertemplate='<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}'
    )
    fig_donut.update_layout(
        showlegend=True,
        margin=dict(t=30, b=20, l=20, r=20),
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig_donut, use_container_width=True)

    # Insight Box 1
    render_insight_box(
        "박스오피스 상위권에 진입한 영화들은 특정 주력 장르(드라마, 액션, 애니메이션 등)에 집중되어 있으며, "
        "장르별 편수 비중을 통해 한국 영화 시장에서 선호되는 주요 장르군과 다변화 정도를 직관적으로 파악할 수 있습니다."
    )


    st.subheader("2. 개봉일 스크린 수와 총 관객 수의 관계")

    fig_scatter_screen = px.scatter(
        filtered_df,
        x='first_scrn',
        y='total_audi',
        color='genre',
        size='first_week_audi',
        hover_name='movieNm',
        hover_data={'first_scrn': ':,', 'total_audi': ':,', 'days_in_top10': True, 'first_week_audi': ':,'},
        labels={
            'first_scrn': '개봉일 스크린 수 (개)',
            'total_audi': '총 관객 수 (명)',
            'genre': '장르',
            'first_week_audi': '개봉 첫주 관객 수'
        },
        opacity=0.85
    )
    fig_scatter_screen.update_layout(
        height=500,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_scatter_screen, use_container_width=True)

    # Insight Box 2
    render_insight_box(
        "개봉일 초기 스크린 확보 수가 많을수록 최종 총 관객 수도 증가하는 뚜렷한 양의 상관관계를 보이지만, "
        "일부 영화는 비교적 적은 스크린으로 시작했음에도 높은 입소문 효과로 총 관객 수 상위권을 기록한 흥행 반전 사례를 확인할 수 있습니다."
    )


    st.subheader("3. 장르별 총 관객 수 분포 및 아웃라이어 (박스플롯)")

    # Filter genres with at least 3 movies for meaningful boxplots
    valid_genres = genre_counts[genre_counts['count'] >= 2]['genre'].tolist()
    df_boxplot = filtered_df[filtered_df['genre'].isin(valid_genres)]

    fig_box = px.box(
        df_boxplot,
        x='genre',
        y='total_audi',
        color='genre',
        points="all",
        hover_name='movieNm',
        labels={'genre': '장르', 'total_audi': '총 관객 수 (명)'}
    )
    fig_box.update_layout(
        showlegend=False,
        height=480,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_box, use_container_width=True)

    # Insight Box 3
    render_insight_box(
        "장르에 따라 총 관객 수의 중앙값뿐만 아니라 산포도(변동성)가 크게 달라지며, "
        "특정 장르에서 상단 이상치(Outlier)로 솟아오른 초대형 대박 영화의 존재 유무와 흥행 안정성을 비교할 수 있습니다."
    )


    st.subheader("4. TOP 10 유지 일수와 흥행 성과의 관계")

    fig_bubble_top10 = px.scatter(
        filtered_df,
        x='days_in_top10',
        y='total_audi',
        size='first_scrn',
        color='nation',
        hover_name='movieNm',
        hover_data={'days_in_top10': True, 'total_audi': ':,', 'first_scrn': ':,'},
        labels={
            'days_in_top10': '10위권 머문 일수 (일)',
            'total_audi': '총 관객 수 (명)',
            'nation': '제작 국가',
            'first_scrn': '개봉일 스크린 수'
        }
    )
    fig_bubble_top10.update_layout(
        height=500,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9')
    )

    st.plotly_chart(fig_bubble_top10, use_container_width=True)

    # Insight Box 4
    render_insight_box(
        "박스오피스 TOP 10에 오래 머물수록(장기 흥행) 총 관객 수가 비례하여 증가하는 경향을 보이며, "
        "초반 스크린 집중 투입으로 빠르게 관객을 모으는 '초반 집중형' 영화와 지속적인 입소문으로 오랜 기간 상위권을 유지하는 '롱런형' 영화의 패턴 구분이 가능합니다."
    )


    st.subheader("5. 흥행 지표 간 상관관계 히트맵")

    num_cols_kr = {
        'first_scrn': '개봉일 스크린수',
        'first_show': '개봉일 상영횟수',
        'first_week_audi': '개봉 첫주 관객수',
        'days_in_top10': 'TOP10 유지일수',
        'total_audi': '총 관객수'
    }
    
    corr_df = filtered_df[list(num_cols_kr.keys())].rename(columns=num_cols_kr).corr()

    fig_corr = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale="Blues",
        aspect="auto",
        labels=dict(color="상관계수")
    )
    fig_corr.update_layout(
        height=420,
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    # Insight Box 5
    render_insight_box(
        "개봉 첫 주 관객 수 및 개봉일 상영 횟수가 최종 총 관객 수와 가장 높은 상관관계를 나타내어, "
        "초반 개봉 주말의 흥행 기세가 영화의 최종 성패를 결정짓는 가장 결정적인 요인임을 알 수 있습니다."
    )


    st.markdown("---")
    st.subheader("📋 상세 데이터 미리보기")
    
    show_cols = ['movieCd', 'movieNm', 'genre', 'nation', 'first_scrn', 'first_show', 'first_week_audi', 'days_in_top10', 'total_audi']
    st.dataframe(
        filtered_df[show_cols].rename(columns={
            'movieCd': '영화코드',
            'movieNm': '영화명',
            'genre': '장르',
            'nation': '제작국가',
            'first_scrn': '개봉일 스크린수',
            'first_show': '개봉일 상영횟수',
            'first_week_audi': '개봉 첫주 관객',
            'days_in_top10': 'TOP10 유지일수',
            'total_audi': '총 관객수'
        }),
        use_container_width=True,
        hide_index=True
    )
