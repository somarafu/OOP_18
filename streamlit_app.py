"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOVA시 스마트시티 자원 배분 시뮬레이터
통합 버전: 기존 대시보드 + 게임형 시뮬레이션 탭

실행:
streamlit run dashboard.py

필요 파일:
- dashboard.py
- classes.py
- requirements.txt

requirements.txt:
streamlit
pandas
plotly
numpy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import math
import os
import sys
import html as html_lib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(__file__))

try:
    from classes import (
        Worker, Student, Caregiver, Unemployed, Elder,
        SolarPanel, HydrogenCell, ESS, ExternalGrid,
        Resource, EnergyGrid, District, City, PolicySimulator,
        budget_to_fulfillment, energy_to_bonus,
        BudgetAllocationError, LowSatisfactionWarning, EnergyAllocationError
    )
except Exception as import_error:
    st.error(
        "classes.py를 불러오지 못했습니다. dashboard.py와 classes.py가 같은 폴더에 있는지 확인해주세요.\n\n"
        f"오류 내용: {import_error}"
    )
    st.stop()

# ──────────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────────
st.set_page_config(
    page_title="NOVA시 스마트시티 시뮬레이터",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────
# 커스텀 CSS
# ──────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #1f2328; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f6f8fa 0%, #ffffff 100%);
    border-right: 1px solid #d0d7de;
}
[data-testid="stSidebar"] .stSlider > div { color: #1f2328; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #1f2328 !important; }

.metric-card {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #0969da; }
.metric-card .label {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #656d76;
    margin-bottom: 8px;
}
.metric-card .value {
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-card .sub { font-size: 12px; color: #656d76; }
.metric-good  { color: #1a7f37; }
.metric-warn  { color: #9a6700; }
.metric-danger{ color: #cf222e; }
.metric-blue  { color: #0969da; }
.metric-purple{ color: #8250df; }

.section-header {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #656d76;
    padding: 8px 0 4px;
    border-bottom: 1px solid #d0d7de;
    margin-bottom: 12px;
}

.alert-danger {
    background: rgba(207, 34, 46, 0.08);
    border: 1px solid rgba(207, 34, 46, 0.3);
    border-left: 4px solid #cf222e;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #82071e;
    font-size: 14px;
}
.alert-success {
    background: rgba(26, 127, 55, 0.08);
    border: 1px solid rgba(26, 127, 55, 0.3);
    border-left: 4px solid #1a7f37;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #0f5323;
    font-size: 14px;
}
.alert-info {
    background: rgba(9, 105, 218, 0.08);
    border: 1px solid rgba(9, 105, 218, 0.3);
    border-left: 4px solid #0969da;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #0550ae;
    font-size: 14px;
}

.stTabs [data-baseweb="tab-list"] {
    background: #f6f8fa;
    border-bottom: 1px solid #d0d7de;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #656d76;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    color: #1f2328 !important;
    border-bottom: 2px solid #0969da;
}

.intro-hero {
    background: linear-gradient(135deg, #0969da 0%, #8250df 100%);
    border-radius: 22px;
    padding: 34px 38px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 16px 38px rgba(9,105,218,0.20);
}
.intro-hero .eyebrow {
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.85;
    margin-bottom: 10px;
}
.intro-hero .title {
    font-size: 34px;
    font-weight: 900;
    line-height: 1.25;
    margin-bottom: 12px;
}
.intro-hero .subtitle {
    font-size: 16px;
    line-height: 1.75;
    opacity: 0.95;
    max-width: 980px;
}
.intro-pills { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
.intro-pill {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.24);
    border-radius: 999px;
    padding: 8px 13px;
    font-size: 13px;
    font-weight: 700;
    color: white;
}
.info-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 8px 22px rgba(27,31,36,0.06);
    height: 100%;
}
.info-card h3 { font-size: 20px; font-weight: 900; color: #1f2328; margin-bottom: 12px; }
.info-card p { font-size: 14px; line-height: 1.75; color: #1f2328; }
.info-card .big-quote {
    font-size: 20px;
    line-height: 1.65;
    font-weight: 900;
    color: #0969da;
    background: #ddf4ff;
    border-left: 5px solid #0969da;
    border-radius: 12px;
    padding: 16px 18px;
    margin: 14px 0;
}
.mini-card {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 16px;
    padding: 18px 18px;
    height: 100%;
}
.mini-card .icon { font-size: 28px; margin-bottom: 8px; }
.mini-card .title { font-size: 16px; font-weight: 900; color: #1f2328; margin-bottom: 7px; }
.mini-card .desc { font-size: 13px; color: #1f2328; line-height: 1.6; }
.scenario-card {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.scenario-badge {
    min-width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
}
.scenario-card-title { font-size: 15px; font-weight: 900; color: #1f2328; margin-bottom: 3px; }
.scenario-card-desc { font-size: 13px; color: #1f2328; line-height: 1.55; }
.check-card {
    background: #f0fff4;
    border: 1px solid #aceebb;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #0f5323;
    font-size: 14px;
    font-weight: 700;
}
.source-card {
    background: #fff8c5;
    border: 1px solid #f0d66b;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.source-card .source-title { font-weight: 900; color: #1f2328; font-size: 14px; margin-bottom: 4px; }
.source-card .source-desc { color: #1f2328; font-size: 13px; line-height: 1.55; }
.flow-box {
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
}
.flow-step { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 14px; }
.flow-num {
    min-width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #0969da;
    color: white;
    font-size: 13px;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
}
.flow-text { font-size: 14px; color: #1f2328; line-height: 1.6; }
.flow-text b { color: #1f2328; }

/* ===== 시각화/표 글씨 가독성 보정: 검정색 고정 ===== */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] *,
[data-testid="stTable"],
[data-testid="stTable"] *,
[data-testid="stMetric"],
[data-testid="stMetric"] *,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] table,
[data-testid="stMarkdownContainer"] table * {
    color: #111827 !important;
}

/* Plotly SVG 텍스트 색상 보정 */
.js-plotly-plot .plotly text,
.js-plotly-plot .main-svg text,
.js-plotly-plot .legend text,
.js-plotly-plot .gtitle,
.js-plotly-plot .xtick text,
.js-plotly-plot .ytick text,
.js-plotly-plot .angularaxistick text,
.js-plotly-plot .radialaxistick text,
.js-plotly-plot .annotation-text {
    fill: #111827 !important;
    color: #111827 !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# 색상 팔레트와 상수
# ──────────────────────────────────────────────────
COLORS = {
    'bg': '#ffffff', 'surface': '#f6f8fa', 'border': '#d0d7de',
    'text': '#1f2328', 'muted': '#656d76',

    # 시각화용 파스텔 팔레트
    # 글씨는 PLOT_LAYOUT/CSS에서 검정 계열을 유지하고,
    # 막대·선·파이·게이지·히트맵 등 수치 색상만 부드럽게 조정합니다.
    'blue': '#8FB7E8',
    'green': '#8FD0A5',
    'yellow': '#F2D16B',
    'red': '#F2A6A6',
    'purple': '#BFA7E8',
    'cyan': '#8FD8D2',

    'districts': ['#8FB7E8', '#8FD0A5', '#F2D16B', '#BFA7E8', '#F2A6A6'],
    'scenarios': ['#8FB7E8', '#8FD0A5', '#BFA7E8', '#8FD8D2', '#F2A6A6'],
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=COLORS['text'], family='Inter, sans-serif', size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    legend=dict(
        bgcolor='rgba(246,248,250,0.9)',
        bordercolor=COLORS['border'],
        borderwidth=1,
        font=dict(size=11, color=COLORS['text']),
    ),
)

DISTRICT_NAMES = [
    'A구역\n(산업단지)', 'B구역\n(대학가)', 'C구역\n(복지타운)',
    'D구역\n(신도시)', 'E구역\n(구도심)',
]
DISTRICT_KEYS = [
    'A구역(산업단지)', 'B구역(대학가)', 'C구역(복지타운)',
    'D구역(신도시)', 'E구역(구도심)'
]
NEED_LABELS = ['건강·안전', '모빌리티', '활동·문화', '기회·교육', '거버넌스']
NEED_KEYS = ['health_safety', 'mobility', 'activities', 'opportunities', 'governance']

# ──────────────────────────────────────────────────
# 도시 초기화
# ──────────────────────────────────────────────────
@st.cache_resource
def get_city():
    worker = Worker()
    student = Student()
    caregiver = Caregiver()
    unemployed = Unemployed()
    elder = Elder()

    districts = [
        District('A구역(산업단지)', {worker: 0.75, student: 0.05, caregiver: 0.08, unemployed: 0.07, elder: 0.05}, 0.45),
        District('B구역(대학가)', {worker: 0.10, student: 0.70, caregiver: 0.08, unemployed: 0.07, elder: 0.05}, 0.42),
        District('C구역(복지타운)', {worker: 0.05, student: 0.03, caregiver: 0.10, unemployed: 0.07, elder: 0.75}, 0.55),
        District('D구역(신도시)', {worker: 0.35, student: 0.25, caregiver: 0.20, unemployed: 0.10, elder: 0.10}, 0.40),
        District('E구역(구도심)', {worker: 0.30, student: 0.05, caregiver: 0.20, unemployed: 0.18, elder: 0.27}, 0.30),
    ]
    return City('NOVA시', districts)

# ──────────────────────────────────────────────────
# 시뮬레이션 실행
# ──────────────────────────────────────────────────
def run_simulation(welfare, education, energy_infra, general_infra, safety, solar, hydrogen, ess, external):
    try:
        resource = Resource(
            welfare=welfare / 100,
            education=education / 100,
            energy_infra=energy_infra / 100,
            general_infra=general_infra / 100,
            safety=safety / 100,
        )
    except BudgetAllocationError as e:
        return None, str(e)

    try:
        grid = EnergyGrid([
            SolarPanel(solar / 100),
            HydrogenCell(hydrogen / 100),
            ESS(ess / 100),
            ExternalGrid(external / 100),
        ])
    except EnergyAllocationError as e:
        return None, str(e)

    city = get_city()
    result = city.apply_policy(resource, grid)
    return result, None

# ──────────────────────────────────────────────────
# 프리셋 시나리오
# ──────────────────────────────────────────────────
PRESETS = {
    '직접 입력': None,
    '초기 상태 (인프라 편중)': dict(welfare=15, education=15, energy_infra=10, general_infra=45, safety=15, solar=10, hydrogen=5, ess=5, external=80),
    '복지 집중': dict(welfare=40, education=15, energy_infra=15, general_infra=20, safety=10, solar=25, hydrogen=15, ess=15, external=45),
    '에너지 자립 집중': dict(welfare=12, education=10, energy_infra=45, general_infra=23, safety=10, solar=45, hydrogen=30, ess=20, external=5),
    '균형 배분': dict(welfare=22, education=20, energy_infra=20, general_infra=23, safety=15, solar=35, hydrogen=25, ess=20, external=20),
    '선순환 최적 ⭐': dict(welfare=20, education=18, energy_infra=30, general_infra=22, safety=10, solar=40, hydrogen=35, ess=20, external=5),
}

# ──────────────────────────────────────────────────
# 공통 평가 함수
# ──────────────────────────────────────────────────
def score_color(score):
    if score < 50:
        return COLORS['red']
    if score < 60:
        return COLORS['yellow']
    if score < 75:
        return COLORS['blue']
    return COLORS['green']


def score_label(score):
    if score < 50:
        return '⚠ 위험'
    if score < 60:
        return '주의'
    if score < 75:
        return '양호'
    return '✅ 우수'


def expected_energy_self_rate(solar, hydrogen, ess, external):
    return (solar * 0.7 + hydrogen * 0.9 + ess * 0.6 + external * 0.0) / 100


def render_allocation_bars(title, desc, items, total):
    st.markdown(f"**{title}**")
    st.caption(desc)

    for label, value, explanation in items:
        left, right = st.columns([0.7, 0.3])
        with left:
            st.write(f"**{label}**")
        with right:
            st.write(f"{value}%")
        st.progress(value / 100)
        st.caption(explanation)

    if total == 100:
        st.success(f"현재 합계: {total}% · 정상")
    else:
        st.error(f"현재 합계: {total}% · 정확히 100%가 되도록 조정 필요")

# ──────────────────────────────────────────────────
# 차트 함수
# ──────────────────────────────────────────────────
def chart_district_bar(result):
    scores = [result['districts'][k] for k in DISTRICT_KEYS]
    colors = [score_color(s) for s in scores]
    labels = [f"{s:.1f}" for s in scores]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=DISTRICT_NAMES,
        y=scores,
        marker_color=colors,
        marker_line_width=0,
        text=labels,
        textposition='outside',
        textfont=dict(size=13, color=COLORS['text']),
        hovertemplate='<b>%{x}</b><br>만족도: %{y:.1f}점<extra></extra>',
    ))
    fig.add_hline(
        y=50,
        line_dash='dot',
        line_color=COLORS['red'],
        line_width=1.5,
        annotation_text='위험 임계치 (50점)',
        annotation_font_color=COLORS['text'],
        annotation_font_size=11,
    )
    fig.add_hline(
        y=75,
        line_dash='dot',
        line_color=COLORS['green'],
        line_width=1,
        annotation_text='우수 기준 (75점)',
        annotation_font_color=COLORS['text'],
        annotation_font_size=11,
    )
    avg = result['city_average']
    fig.add_hline(
        y=avg,
        line_dash='dash',
        line_color=COLORS['purple'],
        line_width=2,
        annotation_text=f'도시 평균 {avg:.1f}점',
        annotation_font_color=COLORS['text'],
        annotation_font_size=12,
        annotation_position='bottom right',
    )
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='구역별 시민 만족도', font=dict(size=14, color=COLORS['text'])),
        yaxis=dict(range=[30, 100], gridcolor=COLORS['border'], gridwidth=0.5, tickfont=dict(color=COLORS['text'])),
        xaxis=dict(tickfont=dict(size=12, color=COLORS['text'])),
        height=340,
    )
    return fig


def chart_need_radar(result, resource):
    need_ratios = resource.get_need_ratios()
    need_scores = [budget_to_fulfillment(need_ratios[k]) for k in NEED_KEYS]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=need_scores + [need_scores[0]],
        theta=NEED_LABELS + [NEED_LABELS[0]],
        fill='toself',
        fillcolor='rgba(143,183,232,0.22)',
        line=dict(color=COLORS['blue'], width=2),
        marker=dict(size=6, color=COLORS['blue']),
        name='니즈 충족도',
        hovertemplate='<b>%{theta}</b><br>%{r:.1f}점<extra></extra>',
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='5개 니즈 충족도', font=dict(size=14, color=COLORS['text'])),
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(range=[0, 100], gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text'], size=10)),
            angularaxis=dict(gridcolor=COLORS['border'], tickfont=dict(color=COLORS['text'], size=12)),
        ),
        height=340,
        showlegend=False,
    )
    return fig


def chart_energy_gauge(rate):
    color = COLORS['red'] if rate < 0.40 else COLORS['yellow'] if rate < 0.60 else COLORS['blue'] if rate < 0.80 else COLORS['green']
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=rate * 100,
        number=dict(suffix='%', font=dict(size=36, color=COLORS['text'])),
        delta=dict(reference=40, valueformat='.1f', font=dict(size=20, color=COLORS['text']), increasing=dict(color='#1A7F37'), decreasing=dict(color='#CF222E')),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor=COLORS['text'], tickfont=dict(color=COLORS['text'], size=10)),
            bar=dict(color=color, thickness=0.25),
            bgcolor='rgba(0,0,0,0)',
            borderwidth=0,
            steps=[
                dict(range=[0, 40], color='rgba(242,166,166,0.34)'),
                dict(range=[40, 60], color='rgba(242,209,107,0.38)'),
                dict(range=[60, 80], color='rgba(143,183,232,0.34)'),
                dict(range=[80, 100], color='rgba(143,208,165,0.36)'),
            ],
            threshold=dict(line=dict(color=COLORS['text'], width=2), thickness=0.75, value=83.13),
        ),
        title=dict(text='에너지 자립률<br><span style="font-size:11px;color:#7d8590">목표: 83.13% (세종시)</span>', font=dict(size=14, color=COLORS['text'])),
    ))
    fig.update_layout(**PLOT_LAYOUT, height=280)
    return fig


def chart_budget_pie(welfare, education, energy_infra, general_infra, safety):
    labels = ['복지', '교육', '에너지\n인프라', '일반\n인프라', '안전']
    values = [welfare, education, energy_infra, general_infra, safety]
    colors_pie = [COLORS['green'], COLORS['blue'], COLORS['yellow'], COLORS['purple'], COLORS['red']]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors_pie, line=dict(color=COLORS['bg'], width=2)),
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>',
        hole=0.45,
        pull=[0.03] * 5,
    ))
    fig.update_layout(
        **{
            **PLOT_LAYOUT,
            'title': dict(text='예산 배분 현황', font=dict(size=14, color=COLORS['text'])),
            'height': 280,
            'showlegend': True,
            'legend': dict(orientation='v', x=1.0, y=0.5, font=dict(size=11, color=COLORS['text']), bgcolor='rgba(0,0,0,0)'),
            'annotations': [dict(text=f'{sum(values)}%', x=0.5, y=0.5, showarrow=False, font=dict(size=16, color=COLORS['text'], family='Inter'))],
        }
    )
    return fig


def chart_energy_pie(solar, hydrogen, ess, external):
    labels = ['태양광', '수소\n연료전지', 'ESS', '외부\n전력망']
    values = [solar, hydrogen, ess, external]
    colors_e = [COLORS['yellow'], COLORS['blue'], COLORS['cyan'], COLORS['muted']]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors_e, line=dict(color=COLORS['bg'], width=2)),
        textfont=dict(size=12, color=COLORS['text']),
        hovertemplate='<b>%{label}</b><br>%{value}%<extra></extra>',
        hole=0.45,
        pull=[0.03] * 4,
    ))
    self_rate = round((solar * 0.7 + hydrogen * 0.9 + ess * 0.6) / 100, 3) * 100
    fig.update_layout(
        **{
            **PLOT_LAYOUT,
            'title': dict(text='에너지원 구성', font=dict(size=14, color=COLORS['text'])),
            'height': 280,
            'showlegend': True,
            'legend': dict(orientation='v', x=1.0, y=0.5, font=dict(size=11, color=COLORS['text']), bgcolor='rgba(0,0,0,0)'),
            'annotations': [dict(text=f'자립<br>{self_rate:.0f}%', x=0.5, y=0.5, showarrow=False, font=dict(size=14, color=COLORS['text'], family='Inter'))],
        }
    )
    return fig


def chart_nonlinear_curve():
    import numpy as np
    x = np.linspace(0, 0.55, 300)
    y = [budget_to_fulfillment(xi) for xi in x]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[xi * 100 for xi in x],
        y=y,
        mode='lines',
        line=dict(color=COLORS['blue'], width=2.5),
        fill='tozeroy',
        fillcolor='rgba(143,183,232,0.16)',
        name='충족도 곡선',
        hovertemplate='예산 %{x:.1f}% → 충족도 %{y:.1f}점<extra></extra>',
    ))
    for rx, label in [(0.10, '40pt'), (0.20, '60pt★'), (0.30, '75pt'), (0.40, '96pt')]:
        ry = budget_to_fulfillment(rx)
        fig.add_trace(go.Scatter(
            x=[rx * 100],
            y=[ry],
            mode='markers+text',
            marker=dict(size=8, color=COLORS['text'], symbol='circle'),
            text=[f'  {rx * 100:.0f}%→{ry:.0f}pt'],
            textposition='middle right',
            textfont=dict(size=11, color=COLORS['text']),
            showlegend=False,
            hoverinfo='skip',
        ))
    fig.add_vline(x=20, line_dash='dot', line_color=COLORS['red'], line_width=1.5, annotation_text='임계점(20%)', annotation_font_color=COLORS['text'], annotation_font_size=12)
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='비선형 변환 함수 — 임계점 효과', font=dict(size=14, color=COLORS['text'])),
        xaxis=dict(title=dict(text='예산 비율 (%)', font=dict(color=COLORS['text'])), tickfont=dict(color=COLORS['text']), gridcolor=COLORS['border']),
        yaxis=dict(title=dict(text='니즈 충족도 점수', font=dict(color=COLORS['text'])), tickfont=dict(color=COLORS['text']), range=[0, 105], gridcolor=COLORS['border']),
        height=280,
        showlegend=False,
    )
    return fig


def chart_scenario_compare(results_dict):
    scenarios = list(results_dict.keys())
    avgs = [results_dict[s]['city_average'] for s in scenarios]
    rates = [results_dict[s]['independence_rate'] * 100 for s in scenarios]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=scenarios,
        y=avgs,
        name='도시 평균 만족도',
        marker_color=[COLORS['blue']] * len(scenarios),
        marker_line_width=0,
        text=[f'{v:.1f}' for v in avgs],
        textposition='outside',
        textfont=dict(size=11, color=COLORS['text']),
        hovertemplate='<b>%{x}</b><br>평균: %{y:.1f}점<extra></extra>',
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=scenarios,
        y=rates,
        name='에너지 자립률',
        mode='lines+markers',
        line=dict(color=COLORS['yellow'], width=2.5),
        marker=dict(size=8, color=COLORS['yellow']),
        hovertemplate='<b>%{x}</b><br>자립률: %{y:.1f}%<extra></extra>',
    ), secondary_y=True)
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='시나리오별 비교 — 만족도 & 에너지 자립률', font=dict(size=14, color=COLORS['text'])),
        height=320,
        xaxis=dict(tickfont=dict(size=11, color=COLORS['text']), title=dict(font=dict(color=COLORS['text'])), gridcolor=COLORS['border']),
    )
    fig.update_yaxes(title_text='도시 평균 만족도', title_font=dict(color=COLORS['text']), tickfont=dict(color=COLORS['text']), range=[40, 85], gridcolor=COLORS['border'], secondary_y=False)
    fig.update_yaxes(title_text='에너지 자립률 (%)', title_font=dict(color=COLORS['text']), tickfont=dict(color=COLORS['text']), range=[0, 100], secondary_y=True)
    return fig


def chart_district_heatmap(results_dict):
    scenarios = list(results_dict.keys())
    z = [[results_dict[s]['districts'][k] for k in DISTRICT_KEYS] for s in scenarios]
    d_labels = ['A (산업단지)', 'B (대학가)', 'C (복지타운)', 'D (신도시)', 'E (구도심)']
    fig = go.Figure(go.Heatmap(
        z=z,
        x=d_labels,
        y=scenarios,
        colorscale='Blues',
        zmin=40,
        zmax=80,
        text=[[f'{v:.1f}' for v in row] for row in z],
        texttemplate='%{text}',
        textfont=dict(size=11, color='black'),
        hovertemplate='시나리오: %{y}<br>구역: %{x}<br>만족도: %{z:.1f}점<extra></extra>',
        colorbar=dict(title=dict(text='점수', font=dict(color=COLORS['text'])), tickfont=dict(color=COLORS['text'])),
    ))
    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='구역별 만족도 히트맵 (시나리오 전체)', font=dict(size=14, color=COLORS['text'])),
        height=320,
        xaxis=dict(tickfont=dict(size=11, color=COLORS['text']), title=dict(font=dict(color=COLORS['text']))),
        yaxis=dict(tickfont=dict(size=11, color=COLORS['text']), title=dict(font=dict(color=COLORS['text']))),
    )
    return fig

# ──────────────────────────────────────────────────
# 게임형 시뮬레이션 탭 함수
# ──────────────────────────────────────────────────
SIM_DISTRICT_INFO = {
    'A구역(산업단지)': {'label': 'A구역 산업단지', 'icon': '🏭', 'desc': '근로자 중심 · 이동성·에너지·인프라 민감', 'x': 70, 'y': 660, 'people': ['👷', '👩‍🏭', '🧑‍💼', '👨‍🔧'], 'weights': {'welfare': 0.45, 'education': 0.35, 'energy_infra': 1.25, 'general_infra': 1.35, 'safety': 0.85}},
    'B구역(대학가)': {'label': 'B구역 대학가', 'icon': '🎓', 'desc': '학생 중심 · 교육·문화·기회 민감', 'x': 260, 'y': 105, 'people': ['🧑‍🎓', '👩‍🎓', '🧑‍💻', '👨‍🎓'], 'weights': {'welfare': 0.35, 'education': 1.60, 'energy_infra': 0.55, 'general_infra': 0.90, 'safety': 0.65}},
    'C구역(복지타운)': {'label': 'C구역 복지타운', 'icon': '🏥', 'desc': '노인·취약계층 중심 · 복지·안전 민감', 'x': 850, 'y': 105, 'people': ['👵', '👴', '👩‍⚕️', '🧓'], 'weights': {'welfare': 1.65, 'education': 0.35, 'energy_infra': 0.55, 'general_infra': 0.70, 'safety': 1.10}},
    'D구역(신도시)': {'label': 'D구역 신도시', 'icon': '🏙️', 'desc': '혼합형 시민 구성 · 균형 정책 반응', 'x': 550, 'y': 660, 'people': ['👨‍👩‍👧', '🧑‍💼', '👩‍💻', '🧑'], 'weights': {'welfare': 0.90, 'education': 0.90, 'energy_infra': 1.05, 'general_infra': 1.05, 'safety': 0.90}},
    'E구역(구도심)': {'label': 'E구역 구도심', 'icon': '🏘️', 'desc': '노후 인프라 · 복지·안전·생활SOC 민감', 'x': 1030, 'y': 660, 'people': ['🧑', '👵', '👴', '👩'], 'weights': {'welfare': 1.15, 'education': 0.55, 'energy_infra': 0.60, 'general_infra': 1.10, 'safety': 1.25}},
}

SIM_BUDGET_ITEMS = {
    'welfare': {'name': '복지', 'item': '힐링 키트', 'icon': '💗', 'object': '🏥', 'color': '#8FD0A5'},
    'education': {'name': '교육', 'item': '지식 스크롤', 'icon': '📘', 'object': '🏫', 'color': '#8FB7E8'},
    'energy_infra': {'name': '에너지 인프라', 'item': '스마트 배터리', 'icon': '🔋', 'object': '🔌', 'color': '#BFA7E8'},
    'general_infra': {'name': '일반 인프라', 'item': '도시 블록', 'icon': '🧱', 'object': '🏞️', 'color': '#F2D16B'},
    'safety': {'name': '안전', 'item': '보호 방패', 'icon': '🛡️', 'object': '👮', 'color': '#F2A6A6'},
}

SIM_ENERGY_ITEMS = {
    'solar': {'name': '태양광', 'icon': '☀️', 'object': '🔆', 'color': '#F2D16B'},
    'hydrogen': {'name': '수소연료전지', 'icon': '💧', 'object': '⚗️', 'color': '#8FB7E8'},
    'ess': {'name': 'ESS', 'icon': '🔋', 'object': '⚡', 'color': '#8FD0A5'},
    'external': {'name': '외부전력망', 'icon': '🗼', 'object': '🔌', 'color': '#C7CDD6'},
}


def sim_clamp(value, low, high):
    return max(low, min(high, value))


def sim_score_face(score):
    if score < 50:
        return '😟'
    if score < 60:
        return '😐'
    if score < 75:
        return '🙂'
    return '😄'


def sim_score_label(score):
    if score < 50:
        return '위험'
    if score < 60:
        return '주의'
    if score < 75:
        return '만족'
    return '매우 만족'


def sim_score_color(score):
    if score < 50:
        return '#E78383'
    if score < 60:
        return '#E5C45E'
    if score < 75:
        return '#7EA8E6'
    return '#78C894'


def sim_score_stars(score):
    if score < 45:
        return '★☆☆☆☆'
    if score < 55:
        return '★★☆☆☆'
    if score < 70:
        return '★★★☆☆'
    if score < 82:
        return '★★★★☆'
    return '★★★★★'


def sim_budget_values(welfare, education, energy_infra, general_infra, safety):
    return {'welfare': welfare, 'education': education, 'energy_infra': energy_infra, 'general_infra': general_infra, 'safety': safety}


def sim_energy_values(solar, hydrogen, ess, external):
    return {'solar': solar, 'hydrogen': hydrogen, 'ess': ess, 'external': external}


def sim_top_budget_items(district_key, budget_values):
    weights = SIM_DISTRICT_INFO[district_key]['weights']
    weighted = [(key, value, value * weights[key]) for key, value in budget_values.items()]
    weighted.sort(key=lambda x: x[2], reverse=True)
    return weighted[:3]


def sim_facilities(district_key, budget_values):
    weights = SIM_DISTRICT_INFO[district_key]['weights']
    weighted_items = []
    for key, value in budget_values.items():
        item = SIM_BUDGET_ITEMS[key]
        count = sim_clamp(round((value * weights[key]) / 24), 1, 3)
        for _ in range(count):
            weighted_items.append((key, item['object'], item['name'], value * weights[key]))
    weighted_items.sort(key=lambda x: x[3], reverse=True)
    return weighted_items[:6]


def sim_comment(score, budget_values):
    top_key = max(budget_values, key=budget_values.get)
    top_name = SIM_BUDGET_ITEMS[top_key]['name']
    if score < 50:
        return '아직 생활이 불편해요', '우리 구역에 필요한 시설이 더 필요해 보여요.'
    if score < 60:
        return '조금 나아졌지만 아쉬워요', f'{top_name} 투입 효과는 보이지만 아직 체감은 제한적이에요.'
    if score < 75:
        return '살기 좋아지고 있어요', f'{top_name} 중심의 정책이 생활환경 개선으로 이어지고 있어요.'
    return '정말 만족스러워요', '필요한 시설과 서비스가 균형 있게 들어와서 체감 만족도가 높아요.'


def sim_applied_items_html(district_key, budget_values):
    html_parts = []
    for key, value, weighted_value in sim_top_budget_items(district_key, budget_values):
        item = SIM_BUDGET_ITEMS[key]
        power = sim_clamp(round(weighted_value), 0, 100)
        html_parts.append(f"""
        <div class="sim-applied-item" style="--item-color:{item['color']};">
            <div class="sim-applied-icon">{item['icon']}</div>
            <div>
                <div class="sim-applied-name">{item['item']}</div>
                <div class="sim-applied-sub">강도 {power}</div>
            </div>
        </div>
        """)
    return ''.join(html_parts)


def sim_facility_html(district_key, budget_values):
    html_parts = []
    for key, icon, name, _ in sim_facilities(district_key, budget_values):
        item = SIM_BUDGET_ITEMS[key]
        html_parts.append(f"""
        <div class="sim-facility-item" style="--item-color:{item['color']};">
            <div class="sim-facility-emoji">{icon}</div>
            <div class="sim-facility-caption">{name}</div>
        </div>
        """)
    return ''.join(html_parts)


def sim_residents_html(district_key, score):
    info = SIM_DISTRICT_INFO[district_key]
    mood = sim_score_face(score)
    html_parts = []
    for i in range(8):
        person = info['people'][i % len(info['people'])]
        html_parts.append(f"""
        <div class="sim-resident-item">
            <div class="sim-resident-person">{person}</div>
            <div class="sim-resident-mood">{mood}</div>
        </div>
        """)
    return ''.join(html_parts)


def sim_district_zone_html(district_key, score, budget_values):
    info = SIM_DISTRICT_INFO[district_key]
    color = sim_score_color(score)
    face = sim_score_face(score)
    label = sim_score_label(score)
    stars = sim_score_stars(score)
    comment_title, comment_text = sim_comment(score, budget_values)

    return f"""
    <div class="sim-district-zone" style="left:{info['x']}px; top:{info['y']}px;">
        <div class="sim-district-header">
            <div class="sim-district-icon">{info['icon']}</div>
            <div>
                <div class="sim-district-title">{info['label']}</div>
                <div class="sim-district-desc">{info['desc']}</div>
            </div>
        </div>
        <div class="sim-applied-panel">
            <div class="sim-panel-title">이 구역에 영향을 준 예산 항목</div>
            <div class="sim-applied-list">{sim_applied_items_html(district_key, budget_values)}</div>
        </div>
        <div class="sim-district-scene">
            <div class="sim-scene-road sim-scene-road-a"></div>
            <div class="sim-scene-road sim-scene-road-b"></div>
            <div class="sim-scene-section">
                <div class="sim-scene-label">시설 변화</div>
                <div class="sim-facility-grid">{sim_facility_html(district_key, budget_values)}</div>
            </div>
            <div class="sim-scene-section">
                <div class="sim-scene-label">주민 반응</div>
                <div class="sim-resident-grid">{sim_residents_html(district_key, score)}</div>
            </div>
        </div>
        <div class="sim-comment-bubble">
            <div class="sim-comment-title">{comment_title}</div>
            <div class="sim-comment-text">{comment_text}</div>
        </div>
        <div class="sim-district-score">
            <div class="sim-score-face">{face}</div>
            <div>
                <div class="sim-score-row">
                    <span class="sim-score-state">{label}</span>
                    <span class="sim-score-stars">{stars}</span>
                </div>
                <div class="sim-score-bar">
                    <div class="sim-score-fill" style="width:{score:.1f}%; background:{color};"></div>
                </div>
            </div>
            <div class="sim-score-num" style="color:{color};">{score:.1f}</div>
        </div>
    </div>
    """


def sim_energy_field_html(energy_values):
    html_parts = []
    for key, value in energy_values.items():
        item = SIM_ENERGY_ITEMS[key]
        count = sim_clamp(round(value / 20), 0, 5)
        objects = ''
        for _ in range(count):
            objects += f"""<div class="sim-energy-object" style="--item-color:{item['color']};">{item['object']}</div>"""
        if count == 0:
            objects = '<div class="sim-energy-empty">투입 없음</div>'
        html_parts.append(f"""
        <div class="sim-energy-card" style="--item-color:{item['color']};">
            <div class="sim-energy-head">
                <div class="sim-energy-icon">{item['icon']}</div>
                <div>
                    <div class="sim-energy-name">{item['name']}</div>
                    <div class="sim-energy-value">{value}%</div>
                </div>
            </div>
            <div class="sim-energy-grid">{objects}</div>
        </div>
        """)
    return ''.join(html_parts)


def render_game_simulation_tab(result, welfare, education, energy_infra, general_infra, safety, solar, hydrogen, ess, external, preset_choice):
    budget_values = sim_budget_values(welfare, education, energy_infra, general_infra, safety)
    energy_values = sim_energy_values(solar, hydrogen, ess, external)

    avg = result['city_average']
    rate = result['independence_rate']
    warnings = result['warnings']

    district_html = ''.join(
        sim_district_zone_html(district_key, result['districts'][district_key], budget_values)
        for district_key in DISTRICT_KEYS
    )

    safe_preset = html_lib.escape(str(preset_choice))
    warning_text = '위험 구역 없음' if not warnings else f'주의 구역 {len(warnings)}개'
    warning_color = '#1a7f37' if not warnings else '#cf222e'

    html = f"""
    <style>
    * {{ box-sizing: border-box; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #ffffff; color: #1f2328; }}
    .sim-root, .sim-root * {{ color: #1f2328; }}
    .sim-applied-icon, .sim-facility-emoji, .sim-energy-icon {{ color: #ffffff !important; }}
    .sim-root {{ width: 100%; padding: 8px 4px 28px; }}
    .sim-hero {{ background: linear-gradient(135deg, #AFC7E8 0%, #B9D9EA 52%, #C7E7E4 100%); border-radius: 24px; padding: 24px 28px; color: #1f2328; margin-bottom: 16px; box-shadow: 0 14px 28px rgba(91,121,153,0.18); }}
    .sim-hero-grid {{ display: grid; grid-template-columns: 1.5fr 1fr; gap: 18px; align-items: center; }}
    .sim-hero-title {{ font-size: 32px; font-weight: 900; line-height: 1.25; margin-bottom: 8px; }}
    .sim-hero-desc {{ font-size: 15px; line-height: 1.7; opacity: 0.95; }}
    .sim-hero-panel {{ background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.24); border-radius: 20px; padding: 14px 16px; }}
    .sim-hero-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.16); font-size: 13px; font-weight: 800; }}
    .sim-hero-row:last-child {{ border-bottom: none; }}
    .sim-hero-value {{ font-size: 16px; font-weight: 900; }}
    .sim-section-title {{ font-size: 22px; font-weight: 900; margin: 18px 0 6px; color: #1f2328; }}
    .sim-section-sub {{ font-size: 13px; color: #1f2328; line-height: 1.6; margin-bottom: 12px; }}
    .sim-village-scroll {{ width: 100%; overflow-x: auto; padding-bottom: 10px; margin-bottom: 22px; }}
    .sim-village-board {{ position: relative; width: 1500px; height: 1240px; border-radius: 30px; overflow: hidden; border: 1px solid #d0d7de; background: linear-gradient(180deg, #eaf5ff 0%, #eef8ff 22%, #edf7e6 55%, #dfeccd 100%); box-shadow: 0 16px 30px rgba(27,31,36,0.08); }}
    .sim-village-title-card {{ position: absolute; left: 24px; top: 24px; width: 340px; background: rgba(255,255,255,0.94); border: 1px solid #d0d7de; border-radius: 20px; padding: 14px 16px; box-shadow: 0 8px 18px rgba(27,31,36,0.07); z-index: 20; }}
    .sim-village-title {{ font-size: 21px; font-weight: 900; margin-bottom: 4px; }}
    .sim-village-desc {{ font-size: 12px; color: #1f2328; line-height: 1.5; }}
    .sim-main-road {{ position: absolute; background: #7b8491; box-shadow: inset 0 0 0 2px rgba(255,255,255,0.15); z-index: 1; pointer-events: none; }}
    .sim-main-road::after {{ content: ""; position: absolute; left: 0; top: 50%; width: 1800px; border-top: 3px dashed rgba(255,255,255,0.72); }}
    .sim-road-1 {{ left: -100px; top: 620px; width: 1800px; height: 42px; transform: rotate(-6deg); }}
    .sim-road-2 {{ left: 500px; top: -90px; width: 48px; height: 1450px; transform: rotate(9deg); }}
    .sim-road-3 {{ left: 990px; top: -90px; width: 48px; height: 1450px; transform: rotate(-10deg); }}
    .sim-water-line {{ position: absolute; left: -80px; bottom: 24px; width: 1700px; height: 70px; transform: rotate(-4deg); background: repeating-linear-gradient(120deg, rgba(255,255,255,0.32) 0 12px, rgba(255,255,255,0.08) 12px 24px), #8ec5ff; border-radius: 999px; z-index: 1; pointer-events: none; }}
    .sim-district-zone {{ position: absolute; width: 390px; height: 490px; background: linear-gradient(180deg, rgba(255,255,255,0.36), rgba(255,255,255,0.20)), repeating-linear-gradient(45deg, #dcedc5 0 18px, #d7e8bf 18px 36px); border: 2px solid rgba(255,255,255,0.95); border-radius: 26px; box-shadow: 0 14px 26px rgba(27,31,36,0.12); overflow: hidden; z-index: 5; padding: 14px; display: flex; flex-direction: column; gap: 10px; }}
    .sim-district-header {{ min-height: 70px; background: rgba(255,255,255,0.98); border: 1px solid #d0d7de; border-radius: 20px; display: grid; grid-template-columns: 50px 1fr; gap: 10px; align-items: center; padding: 10px 12px; box-shadow: 0 6px 12px rgba(27,31,36,0.05); flex-shrink: 0; }}
    .sim-district-icon {{ width: 46px; height: 46px; border-radius: 16px; background: #f6f8fa; display: flex; align-items: center; justify-content: center; font-size: 26px; }}
    .sim-district-title {{ font-size: 18px; font-weight: 900; margin-bottom: 3px; }}
    .sim-district-desc {{ font-size: 12px; color: #1f2328; line-height: 1.35; }}
    .sim-applied-panel {{ min-height: 76px; background: rgba(255,255,255,0.96); border: 1px solid #d0d7de; border-radius: 18px; padding: 9px 10px; box-shadow: 0 5px 10px rgba(27,31,36,0.05); flex-shrink: 0; }}
    .sim-panel-title {{ font-size: 11.5px; font-weight: 900; color: #1f2328; margin-bottom: 7px; }}
    .sim-applied-list {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }}
    .sim-applied-item {{ display: grid; grid-template-columns: 30px 1fr; gap: 7px; align-items: center; min-width: 0; background: #f6f8fa; border: 1px solid #e5e7eb; border-radius: 13px; padding: 6px 7px; }}
    .sim-applied-icon {{ width: 29px; height: 29px; border-radius: 10px; background: var(--item-color); color: white; display: flex; align-items: center; justify-content: center; font-size: 16px; }}
    .sim-applied-name {{ font-size: 11px; font-weight: 900; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .sim-applied-sub {{ font-size: 9.5px; color: #1f2328; }}
    .sim-district-scene {{ position: relative; height: 128px; background: rgba(255,255,255,0.44); border: 1px solid rgba(255,255,255,0.78); border-radius: 18px; overflow: hidden; display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 10px; padding: 10px; flex-shrink: 0; }}
    .sim-scene-road {{ position: absolute; background: rgba(123,132,145,0.55); z-index: 1; pointer-events: none; }}
    .sim-scene-road::after {{ content: ""; position: absolute; left: 0; top: 50%; width: 600px; border-top: 2px dashed rgba(255,255,255,0.68); }}
    .sim-scene-road-a {{ left: -60px; top: 66px; width: 560px; height: 22px; transform: rotate(-6deg); }}
    .sim-scene-road-b {{ left: 190px; top: -40px; width: 22px; height: 220px; transform: rotate(10deg); }}
    .sim-scene-section {{ position: relative; z-index: 5; background: rgba(255,255,255,0.80); border: 1px solid #e5e7eb; border-radius: 16px; padding: 8px; }}
    .sim-scene-label {{ font-size: 10.5px; font-weight: 900; color: #1f2328; margin-bottom: 6px; }}
    .sim-facility-grid, .sim-resident-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }}
    .sim-resident-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .sim-facility-item, .sim-resident-item {{ position: relative; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; min-height: 48px; text-align: center; padding: 5px 3px; box-shadow: 0 3px 7px rgba(27,31,36,0.05); }}
    .sim-resident-item {{ height: 39px; min-height: 39px; display: flex; align-items: center; justify-content: center; }}
    .sim-facility-emoji {{ width: 28px; height: 28px; margin: 0 auto 2px; border-radius: 10px; background: var(--item-color); color: white; display: flex; align-items: center; justify-content: center; font-size: 17px; }}
    .sim-facility-caption {{ font-size: 8.5px; font-weight: 800; color: #1f2328; line-height: 1.1; }}
    .sim-resident-person {{ font-size: 20px; }}
    .sim-resident-mood {{ position: absolute; right: -4px; top: -5px; width: 16px; height: 16px; border-radius: 50%; background: #ffffff; border: 2px solid #d0d7de; display: flex; align-items: center; justify-content: center; font-size: 9px; box-shadow: 0 3px 7px rgba(27,31,36,0.10); }}
    .sim-comment-bubble {{ min-height: 62px; background: rgba(255,255,255,0.97); border: 1px solid #d0d7de; border-radius: 18px; padding: 11px 13px; box-shadow: 0 6px 13px rgba(27,31,36,0.06); flex-shrink: 0; }}
    .sim-comment-title {{ font-size: 14px; font-weight: 900; margin-bottom: 5px; }}
    .sim-comment-text {{ font-size: 12px; color: #1f2328; line-height: 1.4; }}
    .sim-district-score {{ min-height: 66px; background: rgba(255,255,255,0.98); border: 1px solid #d0d7de; border-radius: 20px; display: grid; grid-template-columns: 46px 1fr 70px; gap: 10px; align-items: center; padding: 10px 12px; box-shadow: 0 6px 13px rgba(27,31,36,0.06); flex-shrink: 0; margin-top: auto; }}
    .sim-score-face {{ width: 42px; height: 42px; border-radius: 15px; background: #fff7ed; display: flex; align-items: center; justify-content: center; font-size: 25px; }}
    .sim-score-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
    .sim-score-state {{ font-size: 14px; font-weight: 900; }}
    .sim-score-stars {{ font-size: 12.5px; color: #E5C45E; font-weight: 800; }}
    .sim-score-bar {{ height: 9px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }}
    .sim-score-fill {{ height: 100%; border-radius: 999px; }}
    .sim-score-num {{ font-size: 31px; font-weight: 900; text-align: right; line-height: 1; }}
    .sim-energy-section {{ background: #ffffff; border: 1px solid #d0d7de; border-radius: 24px; padding: 18px; box-shadow: 0 10px 22px rgba(27,31,36,0.06); }}
    .sim-energy-field {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .sim-energy-card {{ border: 1px solid #e5e7eb; border-top: 4px solid var(--item-color); border-radius: 18px; padding: 13px; background: #f8fafc; }}
    .sim-energy-head {{ display: grid; grid-template-columns: 42px 1fr; gap: 9px; align-items: center; margin-bottom: 10px; }}
    .sim-energy-icon {{ width: 40px; height: 40px; border-radius: 14px; background: var(--item-color); color: white; display: flex; align-items: center; justify-content: center; font-size: 23px; }}
    .sim-energy-name {{ font-size: 14px; font-weight: 900; }}
    .sim-energy-value {{ color: var(--item-color); font-size: 12px; font-weight: 900; }}
    .sim-energy-grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 7px; min-height: 84px; }}
    .sim-energy-object {{ background: #ffffff; border: 1px solid #e5e7eb; border-radius: 13px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
    .sim-energy-empty {{ grid-column: 1 / -1; color: #1f2328; font-size: 12px; border: 1px dashed #d0d7de; border-radius: 13px; height: 82px; display: flex; align-items: center; justify-content: center; background: #ffffff; }}
    @media (max-width: 900px) {{ .sim-hero-grid {{ grid-template-columns: 1fr; }} .sim-energy-field {{ grid-template-columns: 1fr; }} }}
    </style>

    <div class="sim-root">
        <div class="sim-hero">
            <div class="sim-hero-grid">
                <div>
                    <div class="sim-hero-title"> NOVA시 게임형 정책 시뮬레이션</div>
                    <div class="sim-hero-desc">
                        왼쪽에서 설정한 예산과 에너지 배분이 A~E구역의 시설, 주민 반응,
                        만족도 댓글로 어떻게 나타나는지 게임 화면처럼 보여줍니다.
                    </div>
                </div>
                <div class="sim-hero-panel">
                    <div class="sim-hero-row"><span>현재 시나리오</span><span class="sim-hero-value">{safe_preset}</span></div>
                    <div class="sim-hero-row"><span>도시 평균 만족도</span><span class="sim-hero-value">{avg:.1f}점</span></div>
                    <div class="sim-hero-row"><span>에너지 자립률</span><span class="sim-hero-value">{rate * 100:.1f}%</span></div>
                    <div class="sim-hero-row"><span>도시 상태</span><span class="sim-hero-value" style="color:{warning_color};">{warning_text}</span></div>
                </div>
            </div>
        </div>

        <div class="sim-section-title">🏘️ NOVA시 통합 마을 지도</div>
        <div class="sim-section-sub">위쪽 행에는 B구역과 C구역, 아래쪽 행에는 A구역·D구역·E구역을 배치해 카드가 겹치지 않도록 구성했습니다.</div>
        <div class="sim-village-scroll">
            <div class="sim-village-board">
                <div class="sim-village-title-card">
                    <div class="sim-village-title">NOVA 통합 마을</div>
                    <div class="sim-village-desc">정책 처치에 따라 구역별 시설과 주민 반응이 달라집니다.</div>
                </div>
                <div class="sim-main-road sim-road-1"></div>
                <div class="sim-main-road sim-road-2"></div>
                <div class="sim-main-road sim-road-3"></div>
                <div class="sim-water-line"></div>
                {district_html}
            </div>
        </div>

        <div class="sim-section-title">⚡ 에너지 아이템 필드</div>
        <div class="sim-section-sub">에너지 배분은 태양광, 수소연료전지, ESS, 외부전력망 오브젝트로 표시됩니다.</div>
        <div class="sim-energy-section"><div class="sim-energy-field">{sim_energy_field_html(energy_values)}</div></div>
    </div>
    """
    components.html(html, height=2050, scrolling=True)

# ──────────────────────────────────────────────────
# 사이드바 — 입력 패널
# ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:16px 0 8px">'
        '<span style="font-size:28px">🏙️</span><br>'
        '<span style="font-size:16px;font-weight:800;color:#1f2328">NOVA시 시뮬레이터</span><br>'
        '<span style="font-size:11px;color:#656d76">Smart City Resource Allocator</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('---')
    st.markdown('<div class="section-header">프리셋 시나리오</div>', unsafe_allow_html=True)
    preset_choice = st.selectbox('', list(PRESETS.keys()), label_visibility='collapsed')
    preset = PRESETS[preset_choice]
    preset_key = preset_choice.replace(' ', '_').replace('(', '').replace(')', '').replace('⭐', 'star')

    def pv(key, default):
        return preset[key] if preset else default

    st.markdown('---')
    st.markdown('<div class="section-header">💰 예산 배분 (%)</div>', unsafe_allow_html=True)
    welfare = st.slider('복지', 0, 100, pv('welfare', 20), 1, key=f'w_{preset_key}')
    education = st.slider('교육', 0, 100, pv('education', 18), 1, key=f'e_{preset_key}')
    energy_infra = st.slider('에너지 인프라', 0, 100, pv('energy_infra', 30), 1, key=f'ei_{preset_key}')
    general_infra = st.slider('일반 인프라', 0, 100, pv('general_infra', 22), 1, key=f'gi_{preset_key}')
    safety = st.slider('안전', 0, 100, pv('safety', 10), 1, key=f's_{preset_key}')
    budget_total = welfare + education + energy_infra + general_infra + safety
    budget_ok = budget_total == 100
    if budget_ok:
        st.markdown(f'<div class="alert-success">합계: {budget_total}% ✓</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-danger">합계: {budget_total}% ← 정확히 100%여야 합니다</div>', unsafe_allow_html=True)

    render_allocation_bars(
        title='예산 배분 조율 항목',
        desc='아래 5개 항목은 시민 만족도를 바꾸는 예산 배분 변수입니다.',
        items=[
            ('복지', welfare, '의료, 돌봄, 노인·취약계층 지원'),
            ('교육', education, '학교, 직업훈련, 청년 기회, 평생학습'),
            ('에너지 인프라', energy_infra, '스마트그리드, 전기차 충전, 친환경 에너지 기반시설'),
            ('일반 인프라', general_infra, '도로, 대중교통, 생활SOC, 공원 등 도시 기반시설'),
            ('안전', safety, '치안, 소방, 재난 대응, CCTV, 교통안전'),
        ],
        total=budget_total,
    )

    st.markdown('---')
    st.markdown('<div class="section-header">⚡ 에너지 배분 (%)</div>', unsafe_allow_html=True)
    solar = st.slider('태양광', 0, 100, pv('solar', 40), 1, key=f'sol_{preset_key}')
    hydrogen = st.slider('수소연료전지', 0, 100, pv('hydrogen', 35), 1, key=f'hyd_{preset_key}')
    ess = st.slider('ESS', 0, 100, pv('ess', 20), 1, key=f'ess_{preset_key}')
    external = st.slider('외부전력망', 0, 100, pv('external', 5), 1, key=f'ext_{preset_key}')
    energy_total = solar + hydrogen + ess + external
    energy_ok = energy_total == 100
    if energy_ok:
        st.markdown(f'<div class="alert-success">합계: {energy_total}% ✓</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-danger">합계: {energy_total}% ← 정확히 100%여야 합니다</div>', unsafe_allow_html=True)

    render_allocation_bars(
        title='에너지 배분 조율 항목',
        desc='아래 4개 항목은 도시의 에너지 자립률을 결정하는 에너지원 구성 변수입니다.',
        items=[
            ('태양광', solar, '설치 비용은 낮지만 날씨와 시간대의 영향을 받음'),
            ('수소연료전지', hydrogen, '안정적 발전이 가능하고 자립률 기여도가 큼'),
            ('ESS', ess, '남는 전력을 저장해 태양광의 불안정성을 보완'),
            ('외부전력망', external, '안정적 공급은 가능하지만 에너지 자립률에는 기여하지 않음'),
        ],
        total=energy_total,
    )
    predicted_rate = expected_energy_self_rate(solar, hydrogen, ess, external)
    st.info(
        f'예상 에너지 자립률: {predicted_rate * 100:.1f}%\n\n'
        '계산식: 태양광×0.7 + 수소연료전지×0.9 + ESS×0.6 + 외부전력망×0.0'
    )
    st.markdown('---')
    run_btn = st.button('▶ 시뮬레이션 실행', type='primary', use_container_width=True)

# ──────────────────────────────────────────────────
# 세션 스테이트 초기화
# ──────────────────────────────────────────────────
if 'result' not in st.session_state:
    st.session_state.result = None
if 'resource_obj' not in st.session_state:
    st.session_state.resource_obj = None
if 'history' not in st.session_state:
    st.session_state.history = {}

# ──────────────────────────────────────────────────
# 실행 버튼 처리
# ──────────────────────────────────────────────────
if run_btn:
    if not budget_ok:
        st.error(f'예산 합계가 {budget_total}%입니다. 정확히 100%로 맞춰주세요.')
    elif not energy_ok:
        st.error(f'에너지 합계가 {energy_total}%입니다. 정확히 100%로 맞춰주세요.')
    else:
        with st.spinner('시뮬레이션 실행 중...'):
            result, err = run_simulation(welfare, education, energy_infra, general_infra, safety, solar, hydrogen, ess, external)
            if err:
                st.error(err)
            else:
                try:
                    r_obj = Resource(welfare / 100, education / 100, energy_infra / 100, general_infra / 100, safety / 100)
                    st.session_state.resource_obj = r_obj
                except Exception:
                    pass
                st.session_state.result = result
                label = preset_choice if preset_choice != '직접 입력' else f'사용자 입력 #{len(st.session_state.history) + 1}'
                st.session_state.history[label] = result

# ──────────────────────────────────────────────────
# 메인 헤더
# ──────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-size:28px;font-weight:800;margin-bottom:4px">🏙️ NOVA시 스마트시티 자원 배분 시뮬레이터</h1>'
    '<p style="color:#7d8590;font-size:14px;margin-top:0">'
    '"기술이 아니라 배분이 도시의 수준을 결정한다"  ·  Social Science & AI융합학부 OOP 프로젝트</p>',
    unsafe_allow_html=True,
)
st.markdown('---')

# ──────────────────────────────────────────────────
# 결과 없을 때 — 안내 화면
# ──────────────────────────────────────────────────
if st.session_state.result is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
<div style="text-align:center;padding:60px 0">
    <div style="font-size:64px;margin-bottom:24px">🏙️</div>
    <div style="font-size:20px;font-weight:700;color:#1f2328;margin-bottom:12px">시뮬레이션을 시작하세요</div>
    <div style="font-size:14px;color:#656d76;line-height:1.8">
        왼쪽 패널에서 프리셋 시나리오를 선택하거나 예산과 에너지 배분 비율을 직접 설정하고<br>
        <b style="color:#0969da">▶ 시뮬레이션 실행</b> 버튼을 누르면<br>
        NOVA시 5개 구역의 시민 만족도가 실시간으로 산출됩니다.
    </div>
    <div style="margin-top:32px;display:flex;justify-content:center;gap:16px;flex-wrap:wrap">
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:12px 20px;font-size:13px;color:#656d76">💰 예산: 복지·교육·에너지·인프라·안전</div>
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:12px 20px;font-size:13px;color:#656d76">⚡ 에너지: 태양광·수소·ESS·외부전력망</div>
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:12px 20px;font-size:13px;color:#656d76">📊 출력: 5개 구역 만족도 + 자립률</div>
    </div>
</div>
        """, unsafe_allow_html=True)
    st.stop()

# ──────────────────────────────────────────────────
# 결과 있을 때 — 대시보드 본문
# ──────────────────────────────────────────────────
result = st.session_state.result
resource_obj = st.session_state.resource_obj

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📊 현황 대시보드',
    '🎮 게임형 시뮬레이션',
    '🔬 시나리오 비교',
    '⚙️ 시스템 분석',
    '📖 프로젝트 소개',
])

# ════════════════════════════════════════════════
# TAB 1: 현황 대시보드
# ════════════════════════════════════════════════
with tab1:
    rate = result['independence_rate']
    avg = result['city_average']
    savings = result['savings']
    warnings = result['warnings']

    r_color = 'metric-good' if rate >= 0.80 else 'metric-blue' if rate >= 0.60 else 'metric-warn' if rate >= 0.40 else 'metric-danger'
    a_color = 'metric-good' if avg >= 75 else 'metric-blue' if avg >= 60 else 'metric-warn' if avg >= 50 else 'metric-danger'

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
<div class="metric-card">
    <div class="label">도시 평균 만족도</div>
    <div class="value {a_color}">{avg:.1f}점</div>
    <div class="sub">{score_label(avg)}</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
<div class="metric-card">
    <div class="label">에너지 자립률</div>
    <div class="value {r_color}">{rate * 100:.1f}%</div>
    <div class="sub">목표: 83.13%</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
<div class="metric-card">
    <div class="label">절감액 환원</div>
    <div class="value metric-purple">{savings * 100:.2f}%</div>
    <div class="sub">복지·교육 재배분</div>
</div>""", unsafe_allow_html=True)
    with c4:
        bonus = energy_to_bonus(rate)
        b_color = 'metric-good' if bonus > 0 else 'metric-danger'
        st.markdown(f"""
<div class="metric-card">
    <div class="label">에너지 만족도 보정</div>
    <div class="value {b_color}">{bonus:+.1f}점</div>
    <div class="sub">자립률 기반 보정값</div>
</div>""", unsafe_allow_html=True)
    with c5:
        n_warn = len(warnings)
        w_color = 'metric-danger' if n_warn > 0 else 'metric-good'
        st.markdown(f"""
<div class="metric-card">
    <div class="label">위험 구역 수</div>
    <div class="value {w_color}">{n_warn}개</div>
    <div class="sub">만족도 50점 미만</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    if warnings:
        for w in warnings:
            st.markdown(f'<div class="alert-danger">🚨 {w}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-success">✅ 모든 구역 안전 구간 — 위험 경보 없음</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.plotly_chart(chart_district_bar(result), use_container_width=True, config={'displayModeBar': False})
    with col_r:
        st.plotly_chart(chart_energy_gauge(rate), use_container_width=True, config={'displayModeBar': False})
        adj = result['adjusted_budget']
        st.markdown(
            f'<div class="alert-info" style="font-size:12px">'
            f'절감액 반영 후 조정 예산<br>'
            f'복지 {adj.welfare * 100:.1f}% / 교육 {adj.education * 100:.1f}% / '
            f'에너지 {adj.energy_infra * 100:.1f}% / 인프라 {adj.general_infra * 100:.1f}%</div>',
            unsafe_allow_html=True,
        )

    col_a, col_b, col_c = st.columns([2, 2, 2])
    with col_a:
        if resource_obj:
            st.plotly_chart(chart_need_radar(result, resource_obj), use_container_width=True, config={'displayModeBar': False})
    with col_b:
        st.plotly_chart(chart_budget_pie(welfare, education, energy_infra, general_infra, safety), use_container_width=True, config={'displayModeBar': False})
    with col_c:
        st.plotly_chart(chart_energy_pie(solar, hydrogen, ess, external), use_container_width=True, config={'displayModeBar': False})

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">구역별 상세 현황</div>', unsafe_allow_html=True)
    rows = []
    for k, name in zip(DISTRICT_KEYS, ['A구역 (산업단지)', 'B구역 (대학가)', 'C구역 (복지타운)', 'D구역 (신도시)', 'E구역 (구도심)']):
        s = result['districts'][k]
        rows.append({'구역': name, '만족도': f'{s:.1f}점', '평가': score_label(s), '게이지': int(s)})
    df = pd.DataFrame(rows)

    def color_row(row):
        s = float(row['만족도'].replace('점', ''))
        c = '#ffebe9' if s < 50 else '#dafbe1' if s >= 75 else '#ddf4ff'
        return [f'background-color:{c};color:#1f2328'] * len(row)

    st.dataframe(df.style.apply(color_row, axis=1), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 2: 게임형 시뮬레이션
# ════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">게임형 정책 시뮬레이션</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="alert-info">
<b>이 탭의 역할</b><br>
왼쪽 사이드바에서 설정한 예산·에너지 배분이 구역별 시설 변화, 주민 반응, 만족도 댓글로 어떻게 나타나는지
게임 화면처럼 보여줍니다. 정량 수치는 현황 대시보드와 동일한 시뮬레이션 결과를 사용합니다.
</div>
    """, unsafe_allow_html=True)
    render_game_simulation_tab(
        result=result,
        welfare=welfare,
        education=education,
        energy_infra=energy_infra,
        general_infra=general_infra,
        safety=safety,
        solar=solar,
        hydrogen=hydrogen,
        ess=ess,
        external=external,
        preset_choice=preset_choice,
    )

# ════════════════════════════════════════════════
# TAB 3: 시나리오 비교
# ════════════════════════════════════════════════
with tab3:
    all_results = {}
    preset_labels = ['초기 상태 (인프라 편중)', '복지 집중', '에너지 자립 집중', '균형 배분', '선순환 최적 ⭐']
    for label in preset_labels:
        p = PRESETS[label]
        r, _ = run_simulation(p['welfare'], p['education'], p['energy_infra'], p['general_infra'], p['safety'], p['solar'], p['hydrogen'], p['ess'], p['external'])
        if r:
            all_results[label.replace(' ⭐', '')] = r
    if result:
        all_results['현재 입력'] = result

    st.plotly_chart(chart_scenario_compare(all_results), use_container_width=True, config={'displayModeBar': False})
    st.plotly_chart(chart_district_heatmap(all_results), use_container_width=True, config={'displayModeBar': False})
    st.markdown('<div class="section-header">시나리오별 수치 비교</div>', unsafe_allow_html=True)
    compare_rows = []
    for name, res in all_results.items():
        compare_rows.append({
            '시나리오': name,
            '도시 평균': f"{res['city_average']:.1f}점",
            '자립률': f"{res['independence_rate'] * 100:.1f}%",
            '절감액': f"{res['savings'] * 100:.2f}%",
            'A구역': f"{res['districts']['A구역(산업단지)']:.1f}",
            'B구역': f"{res['districts']['B구역(대학가)']:.1f}",
            'C구역': f"{res['districts']['C구역(복지타운)']:.1f}",
            'D구역': f"{res['districts']['D구역(신도시)']:.1f}",
            'E구역': f"{res['districts']['E구역(구도심)']:.1f}",
        })
    st.dataframe(pd.DataFrame(compare_rows), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 4: 시스템 분석
# ════════════════════════════════════════════════
with tab4:
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(chart_nonlinear_curve(), use_container_width=True, config={'displayModeBar': False})
        st.markdown("""
<div class="alert-info">
<b>비선형 변환 함수 설명</b><br>
예산 비율이 임계점(20%) 미만이면 서비스가 붕괴 수준으로 하락합니다.
임계점을 넘는 순간 40점 → 60점으로 급상승합니다.
초과 투자 구간에서는 한계효용 체감 법칙에 따라 로그함수로 완만하게 증가합니다.
</div>
        """, unsafe_allow_html=True)
    with col_r:
        import numpy as np
        rates_x = np.linspace(0, 1, 200)
        bonuses = [energy_to_bonus(r) for r in rates_x]
        fig_e = go.Figure()
        fig_e.add_trace(go.Scatter(
            x=[r * 100 for r in rates_x],
            y=bonuses,
            mode='lines',
            line=dict(color=COLORS['yellow'], width=2.5),
            fill='tozeroy',
            fillcolor='rgba(242,209,107,0.18)',
            hovertemplate='자립률 %{x:.1f}% → 보정 %{y:+.1f}점<extra></extra>',
        ))
        fig_e.add_hline(y=0, line_dash='dash', line_color=COLORS['muted'], line_width=1)
        for rx, label in [(0.40, '40% 불안정 구간'), (0.60, '60% 안정 구간'), (0.80, '80% 자립 달성'), (0.8313, '83.13% 세종시 목표')]:
            fig_e.add_vline(x=rx * 100, line_dash='dot', line_color=COLORS['muted'], line_width=1, annotation_text=label, annotation_font_color=COLORS['text'], annotation_font_size=11)
        fig_e.update_layout(
            **PLOT_LAYOUT,
            title=dict(text='에너지 자립률 → 만족도 보정 함수', font=dict(size=14, color=COLORS['text'])),
            xaxis=dict(title=dict(text='에너지 자립률 (%)', font=dict(color=COLORS['text'])), tickfont=dict(color=COLORS['text']), gridcolor=COLORS['border']),
            yaxis=dict(title=dict(text='보정값 (점)', font=dict(color=COLORS['text'])), tickfont=dict(color=COLORS['text']), gridcolor=COLORS['border']),
            height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_e, use_container_width=True, config={'displayModeBar': False})
        st.markdown("""
<div class="alert-info">
<b>에너지 보정 함수 설명</b><br>
자립률 40% 미만: 정전 위험 → 최대 -12점 페널티.<br>
40~60%: 불안정 구간. 60~80%: 안정 구간. 80% 이상: 자립 달성 구간입니다.
</div>
        """, unsafe_allow_html=True)

    st.markdown('---')
    st.markdown('<div class="section-header">OOP 클래스 구조</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="background:#161b22;border:1px solid #21262d;border-radius:10px;padding:20px 24px;font-family:monospace;font-size:13px;color:#e6edf3;line-height:1.8">
<span style="color:#bc8cff">Citizen</span> (부모 클래스) — IMD 5개 니즈 벡터 기반<br>
<span style="color:#7d8590">├──</span> <span style="color:#3fb950">Worker</span>      모빌리티 + 기회 중시<br>
<span style="color:#7d8590">├──</span> <span style="color:#3fb950">Student</span>     교육 + 활동 중시<br>
<span style="color:#7d8590">├──</span> <span style="color:#3fb950">Caregiver</span>   건강·안전 + 거버넌스 중시<br>
<span style="color:#7d8590">├──</span> <span style="color:#3fb950">Unemployed</span>  기회 + 거버넌스 중시<br>
<span style="color:#7d8590">└──</span> <span style="color:#3fb950">Elder</span>       건강·안전 + 모빌리티 중시<br>
<br>
<span style="color:#bc8cff">EnergySource</span> (부모 클래스) — generate() 다형성<br>
<span style="color:#7d8590">├──</span> <span style="color:#388bfd">SolarPanel</span>    실효율 70% · 저비용<br>
<span style="color:#7d8590">├──</span> <span style="color:#388bfd">HydrogenCell</span>  실효율 90% · 24시간 안정<br>
<span style="color:#7d8590">├──</span> <span style="color:#388bfd">ESS</span>           충방전 효율 60% · 태양광 보완<br>
<span style="color:#7d8590">└──</span> <span style="color:#388bfd">ExternalGrid</span>  자립률 기여 0%<br>
<br>
<span style="color:#d29922">District</span>         구역 단위 만족도 계산<br>
<span style="color:#d29922">Resource</span>         예산 배분 + 절감액 재배분<br>
<span style="color:#d29922">EnergyGrid</span>       자립률 계산 + 선순환 절감액 산출<br>
<span style="color:#d29922">City</span>             5개 구역 통합 정책 적용<br>
<span style="color:#d29922">PolicySimulator</span>  시나리오 실행 및 비교
</div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 5: 프로젝트 소개
# ════════════════════════════════════════════════
with tab5:
    st.markdown("""
<div class="intro-hero">
    <div class="eyebrow">NOVA Smart City Simulator</div>
    <div class="title">예산과 에너지 배분이<br>시민 만족도를 어떻게 바꾸는가?</div>
    <div class="subtitle">
        이 프로젝트는 스마트시티를 단순한 기술 인프라의 집합이 아니라,
        제한된 예산과 에너지를 누구에게, 어디에, 어떻게 배분하는지에 따라
        시민의 삶이 달라지는 정책 시뮬레이션 문제로 바라봅니다.
    </div>
    <div class="intro-pills">
        <div class="intro-pill">💰 예산 배분</div>
        <div class="intro-pill">⚡ 에너지 자립률</div>
        <div class="intro-pill">🏘️ 구역별 만족도</div>
        <div class="intro-pill">🔁 선순환 구조</div>
        <div class="intro-pill">⚖️ 트레이드오프</div>
    </div>
</div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.25, 1])
    with col_left:
        st.markdown("""
<div class="info-card">
    <h3>📌 프로젝트 문제의식</h3>
    <p>
        스마트시티 정책은 보통 기술 인프라 중심으로 설명되지만, 실제 시민이 체감하는 도시 만족도는
        기술의 많고 적음만으로 결정되지 않습니다. 제한된 예산을 어떤 구역과 시민 집단에 배분하는지가
        도시 만족도의 핵심 변수가 됩니다.
    </p>
    <div class="big-quote">“기술보다 중요한 것은<br>자원이 어디에 배분되는가이다.”</div>
    <p>
        복지 예산을 늘리면 노인과 취약계층의 만족도는 높아질 수 있지만,
        근로자나 학생의 기회·이동성 만족도는 상대적으로 낮아질 수 있습니다.
        반대로 에너지 인프라에 투자하면 에너지 자립률이 오르고 절감액이 복지·교육으로 환원되는
        선순환이 발생할 수 있습니다.
    </p>
</div>
        """, unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown("""
<div class="flow-box">
    <h3 style="margin-top:0;font-size:20px;font-weight:900;color:#1f2328;">🔄 시뮬레이션 흐름</h3>
    <div class="flow-step"><div class="flow-num">1</div><div class="flow-text"><b>예산 배분 입력</b><br>복지, 교육, 에너지 인프라, 일반 인프라, 안전 비율을 설정합니다.</div></div>
    <div class="flow-step"><div class="flow-num">2</div><div class="flow-text"><b>에너지 배분 입력</b><br>태양광, 수소연료전지, ESS, 외부전력망 비율을 설정합니다.</div></div>
    <div class="flow-step"><div class="flow-num">3</div><div class="flow-text"><b>구역별 시민 구성 반영</b><br>산업단지, 대학가, 복지타운, 신도시, 구도심의 시민 유형 차이를 반영합니다.</div></div>
    <div class="flow-step" style="margin-bottom:0;"><div class="flow-num">4</div><div class="flow-text"><b>만족도와 자립률 산출</b><br>도시 평균 만족도, 위험 구역, 에너지 자립률, 절감액 환원 효과를 계산합니다.</div></div>
</div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("""
<div class="info-card">
    <h3>🎛️ 프리셋 시나리오 가이드</h3>
    <div class="scenario-card"><div class="scenario-badge">🏗️</div><div><div class="scenario-card-title">초기 상태</div><div class="scenario-card-desc">일반 인프라와 외부전력망에 의존하는 기본 상태입니다.</div></div></div>
    <div class="scenario-card"><div class="scenario-badge">🤝</div><div><div class="scenario-card-title">복지 집중</div><div class="scenario-card-desc">복지 예산을 크게 늘려 노인·취약계층 중심 구역의 만족도를 높이는 전략입니다.</div></div></div>
    <div class="scenario-card"><div class="scenario-badge">⚡</div><div><div class="scenario-card-title">에너지 자립 집중</div><div class="scenario-card-desc">에너지 인프라와 신재생에너지 비중을 높여 자립률과 선순환 효과를 강화합니다.</div></div></div>
    <div class="scenario-card"><div class="scenario-badge">⚖️</div><div><div class="scenario-card-title">균형 배분</div><div class="scenario-card-desc">모든 항목을 비교적 고르게 배분하여 극단적 위험 구역을 줄이는 안정형 전략입니다.</div></div></div>
    <div class="scenario-card" style="border-color:#d8b4fe;background:#faf5ff;"><div class="scenario-badge" style="background:#f3e8ff;">⭐</div><div><div class="scenario-card-title">선순환 최적</div><div class="scenario-card-desc">예산 만족도와 에너지 자립률을 동시에 높이는 최적화된 정책 조합입니다.</div></div></div>
</div>
        """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
<div class="mini-card"><div class="icon">👥</div><div class="title">시민 유형 기반</div><div class="desc">근로자, 학생, 돌봄담당자, 실업자, 노인 등 시민 유형별로 중요하게 여기는 도시 니즈가 다르게 설정됩니다.</div></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
<div class="mini-card"><div class="icon">🏘️</div><div class="title">구역별 차이 반영</div><div class="desc">산업단지, 대학가, 복지타운, 신도시, 구도심의 시민 구성이 달라 같은 정책도 다른 결과를 만듭니다.</div></div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
<div class="mini-card"><div class="icon">🔁</div><div class="title">에너지-예산 선순환</div><div class="desc">에너지 자립률이 높아지면 절감액이 발생하고, 일부가 복지·교육 예산으로 환원되는 구조를 반영합니다.</div></div>
        """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("""
<div class="info-card">
    <h3>📚 데이터·근거 출처</h3>
    <div class="source-card"><div class="source-title">IMD Smart City Index 2024/2026</div><div class="source-desc">시민 만족도를 건강·안전, 모빌리티, 활동·문화, 기회·교육, 거버넌스 등 니즈 구조로 해석하는 기준으로 활용했습니다.</div></div>
    <div class="source-card"><div class="source-title">세종시 로렌하우스</div><div class="source-desc">에너지 자립률 목표값 83.13%를 시뮬레이션의 기준선으로 사용했습니다.</div></div>
    <div class="source-card"><div class="source-title">부산 에코델타 스마트빌리지</div><div class="source-desc">태양광, 수소, ESS 등 에너지원 조합 사례를 참고했습니다.</div></div>
    <div class="source-card"><div class="source-title">Shin et al. (2025), J.Policy Stud.</div><div class="source-desc">공급자 중심 스마트시티 정책의 한계와 시민 체감 중심 접근의 필요성을 설명하는 근거로 사용했습니다.</div></div>
</div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
<div class="info-card">
    <h3>✅ 평가 기준</h3>
    <div class="check-card">✅ 시나리오 변화폭이 5점 이상 나타나는가?</div>
    <div class="check-card">✅ 에너지와 예산의 선순환 구조가 작동하는가?</div>
    <div class="check-card">✅ 특정 구역이 소외되는 트레이드오프가 드러나는가?</div>
    <div class="check-card">✅ 선순환 최적 시나리오가 높은 평균 만족도를 보이는가?</div>
    <div class="check-card">✅ OOP 구조가 클래스 상속, 다형성, 예외처리를 충분히 보여주는가?</div>
</div>
        """, unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown("""
<div class="info-card">
    <h3>👩‍💻 프로젝트 정보</h3>
    <p>
        <b>학교</b> 한국외국어대학교<br>
        <b>전공</b> Social Science & AI융합학부<br>
        <b>과목</b> 객체지향형 프로그래밍<br>
        <b>핵심 주제</b> 스마트시티 자원 배분과 시민 만족도 시뮬레이션
    </p>
</div>
        """, unsafe_allow_html=True)
