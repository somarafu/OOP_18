"""
NOVA시 스마트시티 자원 배분 시뮬레이터
Streamlit 대시보드

실행:
streamlit run streamlit_app.py
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys
import os

# classes.py를 같은 폴더에서 import
sys.path.insert(0, os.path.dirname(__file__))

from classes import (
    Worker, Student, Caregiver, Unemployed, Elder,
    SolarPanel, HydrogenCell, ESS, ExternalGrid,
    Resource, EnergyGrid, District, City,
    budget_to_fulfillment, energy_to_bonus,
    BudgetAllocationError, EnergyAllocationError
)

# ==================================================
# 페이지 설정
# ==================================================
st.set_page_config(
    page_title="NOVA시 스마트시티 시뮬레이터",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# CSS
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #1f2328;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f6f8fa 0%, #ffffff 100%);
        border-right: 1px solid #d0d7de;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #1f2328;
    }

    .emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
        font-size: 1.05rem;
        margin-right: 6px;
        vertical-align: -1px;
    }

    .section-header {
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #1f2328;
        padding: 10px 0 6px;
        border-bottom: 1px solid #d0d7de;
        margin-bottom: 12px;
    }

    .section-header .section-text {
        color: #1f2328;
        font-weight: 800;
    }

    .metric-card {
        background: #f6f8fa;
        border: 1px solid #d0d7de;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: border-color 0.2s;
        min-height: 120px;
    }

    .metric-card:hover {
        border-color: #0969da;
    }

    .metric-card .label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #656d76;
        margin-bottom: 8px;
    }

    .metric-card .value {
        font-size: 32px;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 6px;
    }

    .metric-card .sub {
        font-size: 12px;
        color: #656d76;
    }

    .metric-good {
        color: #1a7f37;
    }

    .metric-warn {
        color: #9a6700;
    }

    .metric-danger {
        color: #cf222e;
    }

    .metric-blue {
        color: #0969da;
    }

    .metric-purple {
        color: #8250df;
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

    .allocation-box {
        background: #ffffff;
        border: 1px solid #d0d7de;
        border-radius: 10px;
        padding: 12px 14px;
        margin: 8px 0;
    }

    .allocation-title {
        font-size: 13px;
        font-weight: 800;
        color: #1f2328;
        margin-bottom: 8px;
    }

    .allocation-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 12px;
        color: #1f2328;
        margin: 5px 0 3px;
    }

    .bar-bg {
        background: #eaeef2;
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
    }

    .bar-fill {
        height: 8px;
        border-radius: 999px;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #f6f8fa;
        border-bottom: 1px solid #d0d7de;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #656d76;
        font-weight: 700;
        font-size: 13px;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        color: #1f2328 !important;
        border-bottom: 2px solid #0969da;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 색상 팔레트
# ==================================================
COLORS = {
    "bg": "#ffffff",
    "surface": "#f6f8fa",
    "border": "#d0d7de",
    "text": "#1f2328",
    "muted": "#656d76",
    "blue": "#0969da",
    "green": "#1a7f37",
    "yellow": "#9a6700",
    "red": "#cf222e",
    "purple": "#8250df",
    "cyan": "#1f883d",
    "orange": "#fb8500",
    "gray": "#656d76",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif", size=12),
    margin=dict(l=16, r=16, t=48, b=16),
    legend=dict(
        bgcolor="rgba(246,248,250,0.9)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(size=11, color=COLORS["text"]),
    ),
)

DISTRICT_NAMES = [
    "A구역<br>(산업단지)",
    "B구역<br>(대학가)",
    "C구역<br>(복지타운)",
    "D구역<br>(신도시)",
    "E구역<br>(구도심)",
]

DISTRICT_KEYS = [
    "A구역(산업단지)",
    "B구역(대학가)",
    "C구역(복지타운)",
    "D구역(신도시)",
    "E구역(구도심)",
]

NEED_LABELS = ["건강·안전", "모빌리티", "활동·문화", "기회·교육", "거버넌스"]
NEED_KEYS = ["health_safety", "mobility", "activities", "opportunities", "governance"]

# ==================================================
# 화면 출력 유틸
# ==================================================
def section_header(icon, text):
    return f"""
    <div class="section-header">
        <span class="emoji">{icon}</span>
        <span class="section-text">{text}</span>
    </div>
    """


def normalize_to_percent(values_dict, fallback_value):
    total = sum(values_dict.values())

    if total == 0:
        return {key: fallback_value for key in values_dict.keys()}

    return {
        key: value / total * 100
        for key, value in values_dict.items()
    }


def allocation_progress_box(title, rows):
    """
    rows: [(label, value, color), ...]
    """
    html = f"""
    <div class="allocation-box">
        <div class="allocation-title">{title}</div>
    """

    for label, value, color in rows:
        html += f"""
        <div class="allocation-row">
            <span>{label}</span>
            <strong>{value:.1f}%</strong>
        </div>
        <div class="bar-bg">
            <div class="bar-fill" style="width:{value:.1f}%; background:{color};"></div>
        </div>
        """

    html += "</div>"
    return html


def score_color(score):
    if score < 50:
        return COLORS["red"]
    if score < 60:
        return COLORS["yellow"]
    if score < 75:
        return COLORS["blue"]
    return COLORS["green"]


def score_label(score):
    if score < 50:
        return "위험"
    if score < 60:
        return "주의"
    if score < 75:
        return "양호"
    return "우수"


def metric_class(score):
    if score < 50:
        return "metric-danger"
    if score < 60:
        return "metric-warn"
    if score < 75:
        return "metric-blue"
    return "metric-good"


def energy_status(rate):
    if rate < 0.40:
        return "위험", COLORS["red"]
    if rate < 0.60:
        return "불안정", COLORS["yellow"]
    if rate < 0.80:
        return "안정", COLORS["blue"]
    return "자립 우수", COLORS["green"]

# ==================================================
# 도시 초기화
# ==================================================
@st.cache_resource
def get_city():
    worker = Worker()
    student = Student()
    caregiver = Caregiver()
    unemployed = Unemployed()
    elder = Elder()

    districts = [
        District(
            "A구역(산업단지)",
            {worker: 0.75, student: 0.05, caregiver: 0.08, unemployed: 0.07, elder: 0.05},
            0.45,
        ),
        District(
            "B구역(대학가)",
            {worker: 0.10, student: 0.70, caregiver: 0.08, unemployed: 0.07, elder: 0.05},
            0.42,
        ),
        District(
            "C구역(복지타운)",
            {worker: 0.05, student: 0.03, caregiver: 0.10, unemployed: 0.07, elder: 0.75},
            0.55,
        ),
        District(
            "D구역(신도시)",
            {worker: 0.35, student: 0.25, caregiver: 0.20, unemployed: 0.10, elder: 0.10},
            0.40,
        ),
        District(
            "E구역(구도심)",
            {worker: 0.30, student: 0.05, caregiver: 0.20, unemployed: 0.18, elder: 0.27},
            0.30,
        ),
    ]

    return City("NOVA시", districts)

# ==================================================
# 시뮬레이션 실행
# ==================================================
def run_simulation(
    welfare,
    education,
    energy_infra,
    general_infra,
    safety,
    solar,
    hydrogen,
    ess,
    external,
):
    try:
        resource = Resource(
            welfare=welfare / 100,
            education=education / 100,
            energy_infra=energy_infra / 100,
            general_infra=general_infra / 100,
            safety=safety / 100,
        )
    except BudgetAllocationError as e:
        return None, None, str(e)

    try:
        grid = EnergyGrid(
            [
                SolarPanel(solar / 100),
                HydrogenCell(hydrogen / 100),
                ESS(ess / 100),
                ExternalGrid(external / 100),
            ]
        )
    except EnergyAllocationError as e:
        return None, None, str(e)

    city = get_city()
    result = city.apply_policy(resource, grid)

    return result, resource, None

# ==================================================
# 프리셋
# ==================================================
PRESETS = {
    "직접 입력": None,
    "초기 상태: 인프라 편중": dict(
        welfare=15,
        education=15,
        energy_infra=10,
        general_infra=45,
        safety=15,
        solar=10,
        hydrogen=5,
        ess=5,
        external=80,
    ),
    "복지 집중": dict(
        welfare=40,
        education=15,
        energy_infra=15,
        general_infra=20,
        safety=10,
        solar=25,
        hydrogen=15,
        ess=15,
        external=45,
    ),
    "에너지 자립 집중": dict(
        welfare=12,
        education=10,
        energy_infra=45,
        general_infra=23,
        safety=10,
        solar=45,
        hydrogen=30,
        ess=20,
        external=5,
    ),
    "균형 배분": dict(
        welfare=22,
        education=20,
        energy_infra=20,
        general_infra=23,
        safety=15,
        solar=35,
        hydrogen=25,
        ess=20,
        external=20,
    ),
    "선순환 최적": dict(
        welfare=20,
        education=18,
        energy_infra=30,
        general_infra=22,
        safety=10,
        solar=40,
        hydrogen=35,
        ess=20,
        external=5,
    ),
}

# ==================================================
# 차트 함수
# ==================================================
def chart_district_bar(result):
    scores = [result["districts"][k] for k in DISTRICT_KEYS]
    colors = [score_color(s) for s in scores]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=DISTRICT_NAMES,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
            textfont=dict(size=13, color=COLORS["text"]),
            hovertemplate="<b>%{x}</b><br>만족도: %{y:.1f}점<extra></extra>",
        )
    )

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color=COLORS["red"],
        line_width=1.5,
        annotation_text="위험 임계치 50점",
        annotation_font_color=COLORS["red"],
    )

    fig.add_hline(
        y=75,
        line_dash="dot",
        line_color=COLORS["green"],
        line_width=1,
        annotation_text="우수 기준 75점",
        annotation_font_color=COLORS["green"],
    )

    avg = result["city_average"]

    fig.add_hline(
        y=avg,
        line_dash="dash",
        line_color=COLORS["purple"],
        line_width=2,
        annotation_text=f"도시 평균 {avg:.1f}점",
        annotation_font_color=COLORS["purple"],
        annotation_position="bottom right",
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="구역별 시민 만족도", font=dict(size=16, color=COLORS["text"])),
        yaxis=dict(
            range=[30, 100],
            gridcolor=COLORS["border"],
            tickfont=dict(color=COLORS["muted"]),
            title="만족도 점수",
        ),
        xaxis=dict(tickfont=dict(size=12, color=COLORS["text"])),
        height=360,
        showlegend=False,
    )

    return fig


def chart_need_radar(resource):
    need_ratios = resource.get_need_ratios()
    need_scores = [budget_to_fulfillment(need_ratios[k]) for k in NEED_KEYS]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=need_scores + [need_scores[0]],
            theta=NEED_LABELS + [NEED_LABELS[0]],
            fill="toself",
            fillcolor="rgba(9,105,218,0.15)",
            line=dict(color=COLORS["blue"], width=2),
            marker=dict(size=6, color=COLORS["blue"]),
            name="니즈 충족도",
            hovertemplate="<b>%{theta}</b><br>%{r:.1f}점<extra></extra>",
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="5개 시민 니즈 충족도", font=dict(size=16, color=COLORS["text"])),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                range=[0, 100],
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["muted"], size=10),
            ),
            angularaxis=dict(
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["text"], size=12),
            ),
        ),
        height=360,
        showlegend=False,
    )

    return fig


def chart_energy_gauge(rate):
    value = rate * 100
    label, color = energy_status(rate)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            number=dict(suffix="%", font=dict(size=36, color=color)),
            delta=dict(
                reference=40,
                valueformat=".1f",
                increasing=dict(color=COLORS["green"]),
                decreasing=dict(color=COLORS["red"]),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, 100],
                    tickwidth=1,
                    tickcolor=COLORS["muted"],
                    tickfont=dict(color=COLORS["muted"], size=10),
                ),
                bar=dict(color=color, thickness=0.25),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                steps=[
                    dict(range=[0, 40], color="rgba(207,34,46,0.15)"),
                    dict(range=[40, 60], color="rgba(154,103,0,0.15)"),
                    dict(range=[60, 80], color="rgba(9,105,218,0.15)"),
                    dict(range=[80, 100], color="rgba(26,127,55,0.15)"),
                ],
                threshold=dict(
                    line=dict(color=COLORS["text"], width=2),
                    thickness=0.75,
                    value=83.13,
                ),
            ),
            title=dict(
                text=f'에너지 자립률<br><span style="font-size:11px;color:#656d76">상태: {label} · 목표 기준 83.13%</span>',
                font=dict(size=14, color=COLORS["text"]),
            ),
        )
    )

    fig.update_layout(**PLOT_LAYOUT, height=300)
    return fig


def chart_budget_pie(welfare, education, energy_infra, general_infra, safety):
    labels = ["복지", "교육", "에너지 인프라", "일반 인프라", "안전"]
    values = [welfare, education, energy_infra, general_infra, safety]
    colors_pie = [COLORS["green"], COLORS["blue"], COLORS["yellow"], COLORS["purple"], COLORS["red"]]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors_pie, line=dict(color=COLORS["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            hole=0.45,
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="예산 배분 구성", font=dict(size=16, color=COLORS["text"])),
        height=310,
        annotations=[
            dict(
                text="예산<br>100%",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=COLORS["text"]),
            )
        ],
    )

    return fig


def chart_energy_pie(solar, hydrogen, ess, external):
    labels = ["태양광", "수소연료전지", "ESS", "외부전력망"]
    values = [solar, hydrogen, ess, external]
    colors_e = [COLORS["orange"], COLORS["blue"], COLORS["cyan"], COLORS["gray"]]

    self_rate = (solar * 0.7 + hydrogen * 0.9 + ess * 0.6) / 100

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors_e, line=dict(color=COLORS["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            hole=0.45,
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="에너지 배분 구성", font=dict(size=16, color=COLORS["text"])),
        height=310,
        annotations=[
            dict(
                text=f"자립<br>{self_rate*100:.1f}%",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=COLORS["text"]),
            )
        ],
    )

    return fig


def chart_energy_bar(solar, hydrogen, ess, external):
    labels = ["태양광", "수소연료전지", "ESS", "외부전력망"]
    values = [solar, hydrogen, ess, external]
    contribution = [solar * 0.7 / 100, hydrogen * 0.9 / 100, ess * 0.6 / 100, 0]
    contribution_pct = [v * 100 for v in contribution]
    colors = [COLORS["orange"], COLORS["blue"], COLORS["cyan"], COLORS["gray"]]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            name="구성 비율",
            marker_color=colors,
            text=[f"{v:.1f}%" for v in values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>구성 비율: %{y:.1f}%<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=contribution_pct,
            name="자립률 기여",
            mode="lines+markers",
            line=dict(color=COLORS["red"], width=3),
            marker=dict(size=9),
            hovertemplate="<b>%{x}</b><br>자립률 기여: %{y:.1f}%p<extra></extra>",
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="에너지원별 구성 비율과 자립률 기여", font=dict(size=16)),
        yaxis=dict(
            title="비율 또는 기여도(%)",
            range=[0, 100],
            gridcolor=COLORS["border"],
        ),
        xaxis=dict(tickfont=dict(color=COLORS["text"])),
        height=340,
        legend=dict(orientation="h", y=-0.15),
    )

    return fig


def chart_nonlinear_curve():
    x = np.linspace(0, 0.55, 300)
    y = [budget_to_fulfillment(xi) for xi in x]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[xi * 100 for xi in x],
            y=y,
            mode="lines",
            line=dict(color=COLORS["blue"], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(9,105,218,0.08)",
            name="충족도 곡선",
            hovertemplate="예산 %{x:.1f}% → 충족도 %{y:.1f}점<extra></extra>",
        )
    )

    fig.add_vline(
        x=20,
        line_dash="dot",
        line_color=COLORS["red"],
        annotation_text="임계점 20%",
        annotation_font_color=COLORS["red"],
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="예산 비율 → 니즈 충족도 비선형 변환", font=dict(size=16)),
        xaxis=dict(
            title="예산 비율 (%)",
            gridcolor=COLORS["border"],
            tickfont=dict(color=COLORS["muted"]),
        ),
        yaxis=dict(
            title="니즈 충족도 점수",
            range=[0, 105],
            gridcolor=COLORS["border"],
            tickfont=dict(color=COLORS["muted"]),
        ),
        height=320,
        showlegend=False,
    )

    return fig


def chart_scenario_compare(results_dict):
    scenarios = list(results_dict.keys())
    avgs = [results_dict[s]["city_average"] for s in scenarios]
    rates = [results_dict[s]["independence_rate"] * 100 for s in scenarios]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=scenarios,
            y=avgs,
            name="도시 평균 만족도",
            marker_color=COLORS["blue"],
            text=[f"{v:.1f}" for v in avgs],
            textposition="outside",
            textfont=dict(color=COLORS["text"]),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=scenarios,
            y=rates,
            name="에너지 자립률",
            mode="lines+markers",
            line=dict(color=COLORS["yellow"], width=3),
            marker=dict(size=9),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="시나리오별 만족도와 에너지 자립률 비교", font=dict(size=16)),
        height=360,
    )

    fig.update_yaxes(
        title_text="도시 평균 만족도",
        range=[40, 90],
        secondary_y=False,
        gridcolor=COLORS["border"],
    )

    fig.update_yaxes(
        title_text="에너지 자립률 (%)",
        range=[0, 100],
        secondary_y=True,
    )

    return fig


def chart_district_heatmap(results_dict):
    scenarios = list(results_dict.keys())

    z = [
        [results_dict[s]["districts"][k] for k in DISTRICT_KEYS]
        for s in scenarios
    ]

    d_labels = ["A 산업단지", "B 대학가", "C 복지타운", "D 신도시", "E 구도심"]

    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=d_labels,
            y=scenarios,
            colorscale="Blues",
            zmin=40,
            zmax=85,
            text=[[f"{v:.1f}" for v in row] for row in z],
            texttemplate="%{text}",
            textfont=dict(size=12, color=COLORS["text"]),
            hovertemplate="시나리오: %{y}<br>구역: %{x}<br>만족도: %{z:.1f}점<extra></extra>",
            colorbar=dict(title="점수"),
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        title=dict(text="시나리오별 구역 만족도 히트맵", font=dict(size=16)),
        height=360,
    )

    return fig

# ==================================================
# 사이드바
# ==================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:16px 0 8px">
            <span class="emoji" style="font-size:28px">🏙️</span><br>
            <span style="font-size:16px;font-weight:800;color:#1f2328">
            NOVA시 시뮬레이터</span><br>
            <span style="font-size:11px;color:#656d76">
            Smart City Resource Allocator</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        section_header("🎛️", "프리셋 시나리오"),
        unsafe_allow_html=True,
    )

    preset_choice = st.selectbox(
        "시나리오 선택",
        list(PRESETS.keys()),
        label_visibility="collapsed",
    )

    preset = PRESETS[preset_choice]

    def pv(key, default):
        return preset[key] if preset else default

    st.markdown("---")

    # ==================================================
    # 예산 배분 우선도
    # ==================================================
    st.markdown(
        section_header("💰", "예산 배분 우선도"),
        unsafe_allow_html=True,
    )

    st.caption(
        "슬라이더 값은 직접적인 퍼센트가 아니라 정책 우선도입니다. "
        "값이 클수록 해당 분야의 예산 비중이 커지며, 앱이 자동으로 합계 100%로 변환합니다."
    )

    with st.expander("💡 예산 항목 설명 보기", expanded=False):
        st.markdown(
            """
            - **복지**: 의료, 돌봄, 노인·취약계층 지원과 관련됩니다.  
              → 건강·안전, 활동·문화, 거버넌스 만족도에 영향을 줍니다.

            - **교육**: 학교, 직업훈련, 평생학습, 청년 기회와 관련됩니다.  
              → 기회·교육, 활동·문화 만족도에 영향을 줍니다.

            - **에너지 인프라**: 스마트그리드, 전기차 충전, 친환경 에너지 기반시설과 관련됩니다.  
              → 거버넌스, 모빌리티, 건강·안전에 영향을 줍니다.

            - **일반 인프라**: 도로, 대중교통, 생활SOC, 공원 등 도시 기반시설입니다.  
              → 모빌리티, 건강·안전, 활동·문화에 영향을 줍니다.

            - **안전**: 치안, 소방, 재난 대응, CCTV, 교통안전과 관련됩니다.  
              → 건강·안전, 거버넌스, 모빌리티에 영향을 줍니다.
            """
        )

    welfare_priority = st.slider(
        "복지 우선도",
        0,
        100,
        pv("welfare", 20),
        1,
        help="값이 높을수록 복지, 의료, 돌봄 관련 예산 비중이 커집니다.",
    )

    education_priority = st.slider(
        "교육 우선도",
        0,
        100,
        pv("education", 18),
        1,
        help="값이 높을수록 교육, 직업훈련, 청년 기회 관련 예산 비중이 커집니다.",
    )

    energy_infra_priority = st.slider(
        "에너지 인프라 우선도",
        0,
        100,
        pv("energy_infra", 30),
        1,
        help="값이 높을수록 스마트그리드, 전기차 충전, 신재생에너지 인프라 투자가 커집니다.",
    )

    general_infra_priority = st.slider(
        "일반 인프라 우선도",
        0,
        100,
        pv("general_infra", 22),
        1,
        help="값이 높을수록 도로, 대중교통, 생활SOC 등 일반 인프라 투자가 커집니다.",
    )

    safety_priority = st.slider(
        "안전 우선도",
        0,
        100,
        pv("safety", 10),
        1,
        help="값이 높을수록 치안, 소방, 재난 대응, 교통안전 투자가 커집니다.",
    )

    budget_priorities = {
        "welfare": welfare_priority,
        "education": education_priority,
        "energy_infra": energy_infra_priority,
        "general_infra": general_infra_priority,
        "safety": safety_priority,
    }

    budget_percent = normalize_to_percent(budget_priorities, fallback_value=20.0)

    welfare = budget_percent["welfare"]
    education = budget_percent["education"]
    energy_infra = budget_percent["energy_infra"]
    general_infra = budget_percent["general_infra"]
    safety = budget_percent["safety"]

    budget_total = welfare + education + energy_infra + general_infra + safety

    st.markdown(
        allocation_progress_box(
            "자동 변환된 예산 배분",
            [
                ("복지", welfare, COLORS["green"]),
                ("교육", education, COLORS["blue"]),
                ("에너지 인프라", energy_infra, COLORS["yellow"]),
                ("일반 인프라", general_infra, COLORS["purple"]),
                ("안전", safety, COLORS["red"]),
            ],
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="alert-success">
            <b>예산 배분 합계</b>: {budget_total:.1f}%<br>
            입력한 우선도를 기준으로 자동 정규화되었습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ==================================================
    # 에너지 배분 우선도
    # ==================================================
    st.markdown(
        section_header("⚡", "에너지 배분 우선도"),
        unsafe_allow_html=True,
    )

    st.caption(
        "슬라이더 값은 직접적인 퍼센트가 아니라 에너지원 구성 우선도입니다. "
        "값이 클수록 해당 에너지원 비중이 커지며, 앱이 자동으로 합계 100%로 변환합니다."
    )

    with st.expander("💡 에너지원 설명 보기", expanded=False):
        st.markdown(
            """
            - **태양광**: 설치 비용은 낮지만 날씨와 시간대의 영향을 받습니다.  
              → 자립률에 중간 수준으로 기여합니다.

            - **수소연료전지**: 24시간 안정적으로 발전할 수 있지만 비용이 높습니다.  
              → 자립률에 크게 기여합니다.

            - **ESS**: 남는 전력을 저장했다가 필요할 때 쓰는 배터리 시스템입니다.  
              → 태양광의 불안정성을 보완합니다.

            - **외부전력망**: 안정적으로 전기를 공급받지만 도시 자체의 에너지 자립률에는 기여하지 않습니다.  
              → 비중이 높을수록 자립형 스마트시티와는 멀어집니다.
            """
        )

    solar_priority = st.slider(
        "태양광 우선도",
        0,
        100,
        pv("solar", 40),
        1,
        help="값이 높을수록 태양광 발전 비중이 커집니다.",
    )

    hydrogen_priority = st.slider(
        "수소연료전지 우선도",
        0,
        100,
        pv("hydrogen", 35),
        1,
        help="값이 높을수록 수소연료전지 비중이 커집니다.",
    )

    ess_priority = st.slider(
        "ESS 우선도",
        0,
        100,
        pv("ess", 20),
        1,
        help="값이 높을수록 에너지 저장장치 비중이 커집니다.",
    )

    external_priority = st.slider(
        "외부전력망 의존도",
        0,
        100,
        pv("external", 5),
        1,
        help="값이 높을수록 외부 전력망 의존도가 커집니다. 자립률에는 기여하지 않습니다.",
    )

    energy_priorities = {
        "solar": solar_priority,
        "hydrogen": hydrogen_priority,
        "ess": ess_priority,
        "external": external_priority,
    }

    energy_percent = normalize_to_percent(energy_priorities, fallback_value=25.0)

    solar = energy_percent["solar"]
    hydrogen = energy_percent["hydrogen"]
    ess = energy_percent["ess"]
    external = energy_percent["external"]

    energy_total = solar + hydrogen + ess + external
    expected_self_rate = (solar * 0.7 + hydrogen * 0.9 + ess * 0.6) / 100
    expected_label, expected_color = energy_status(expected_self_rate)

    st.markdown(
        allocation_progress_box(
            "자동 변환된 에너지 배분",
            [
                ("태양광", solar, COLORS["orange"]),
                ("수소연료전지", hydrogen, COLORS["blue"]),
                ("ESS", ess, COLORS["cyan"]),
                ("외부전력망", external, COLORS["gray"]),
            ],
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="alert-info">
            <b>에너지 배분 합계</b>: {energy_total:.1f}%<br>
            <b>예상 에너지 자립률</b>: 
            <span style="color:{expected_color}; font-weight:800">{expected_self_rate*100:.1f}%</span>
            · 상태: <b>{expected_label}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    run_btn = st.button(
        "▶ 시뮬레이션 실행",
        type="primary",
        use_container_width=True,
    )

# ==================================================
# 세션 상태 초기화
# ==================================================
if "result" not in st.session_state:
    st.session_state.result = None

if "resource_obj" not in st.session_state:
    st.session_state.resource_obj = None

if "history" not in st.session_state:
    st.session_state.history = {}

if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = {}

# ==================================================
# 버튼 실행 처리
# ==================================================
if run_btn:
    with st.spinner("시뮬레이션 실행 중..."):
        result, resource_obj, err = run_simulation(
            welfare,
            education,
            energy_infra,
            general_infra,
            safety,
            solar,
            hydrogen,
            ess,
            external,
        )

        if err:
            st.error(err)
        else:
            st.session_state.result = result
            st.session_state.resource_obj = resource_obj
            st.session_state.last_inputs = {
                "welfare": welfare,
                "education": education,
                "energy_infra": energy_infra,
                "general_infra": general_infra,
                "safety": safety,
                "solar": solar,
                "hydrogen": hydrogen,
                "ess": ess,
                "external": external,
            }

            label = (
                preset_choice
                if preset_choice != "직접 입력"
                else f"사용자 입력 #{len(st.session_state.history) + 1}"
            )

            st.session_state.history[label] = result

# ==================================================
# 메인 헤더
# ==================================================
st.markdown(
    """
    <h1 style="font-size:30px;font-weight:800;margin-bottom:4px">
        🏙️ NOVA시 스마트시티 자원 배분 시뮬레이터
    </h1>
    <p style="color:#656d76;font-size:14px;margin-top:0">
        "기술이 아니라 배분이 도시의 수준을 결정한다" · 
        예산 배분과 에너지 배분에 따른 시민 만족도 변화 시뮬레이션
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ==================================================
# 결과 없을 때 안내 화면
# ==================================================
if st.session_state.result is None:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 0">
                <div style="font-size:56px;margin-bottom:24px">🏙️ NOVA</div>
                <div style="font-size:20px;font-weight:700;color:#1f2328;margin-bottom:12px">
                    시뮬레이션을 시작하세요
                </div>
                <div style="font-size:14px;color:#656d76;line-height:1.8">
                    왼쪽 패널에서 <b>예산 배분 우선도</b>와 <b>에너지 배분 우선도</b>를 조정한 뒤<br>
                    <b style="color:#0969da">시뮬레이션 실행</b> 버튼을 누르면<br>
                    NOVA시 5개 구역의 시민 만족도와 에너지 자립률이 계산됩니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()

# ==================================================
# 결과 대시보드
# ==================================================
result = st.session_state.result
resource_obj = st.session_state.resource_obj
last_inputs = st.session_state.last_inputs

city_avg = result["city_average"]
energy_rate = result["independence_rate"]
energy_bonus = energy_to_bonus(energy_rate)
energy_label, energy_color = energy_status(energy_rate)

danger_zones = [
    k for k, v in result["districts"].items()
    if v < 50
]

# ==================================================
# KPI 카드
# ==================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">도시 평균 만족도</div>
            <div class="value {metric_class(city_avg)}">{city_avg:.1f}점</div>
            <div class="sub">{score_label(city_avg)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">에너지 자립률</div>
            <div class="value" style="color:{energy_color}">{energy_rate*100:.1f}%</div>
            <div class="sub">{energy_label} · 만족도 보정 {energy_bonus:+.1f}점</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    if danger_zones:
        danger_text = f"{len(danger_zones)}개"
        danger_class = "metric-danger"
        danger_sub = ", ".join(danger_zones)
    else:
        danger_text = "0개"
        danger_class = "metric-good"
        danger_sub = "위험 구역 없음"

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">위험 구역</div>
            <div class="value {danger_class}">{danger_text}</div>
            <div class="sub">{danger_sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    scores = list(result["districts"].values())
    gap = max(scores) - min(scores)

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">구역 간 격차</div>
            <div class="value metric-purple">{gap:.1f}점</div>
            <div class="sub">최고 - 최저 만족도</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ==================================================
# 탭 구성
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 현황 대시보드",
        "⚡ 에너지 분석",
        "🔬 시나리오 비교",
        "📖 프로젝트 소개",
    ]
)

# ==================================================
# TAB 1: 현황 대시보드
# ==================================================
with tab1:
    if danger_zones:
        st.markdown(
            f"""
            <div class="alert-danger">
                <b>⚠️ 위험 경보</b><br>
                다음 구역의 만족도가 50점 미만입니다: {", ".join(danger_zones)}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="alert-success">
                <b>✅ 안정 상태</b><br>
                현재 모든 구역의 만족도가 위험 기준선인 50점 이상입니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.plotly_chart(chart_district_bar(result), use_container_width=True)

    with col_right:
        st.plotly_chart(chart_energy_gauge(energy_rate), use_container_width=True)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.plotly_chart(
            chart_budget_pie(
                last_inputs["welfare"],
                last_inputs["education"],
                last_inputs["energy_infra"],
                last_inputs["general_infra"],
                last_inputs["safety"],
            ),
            use_container_width=True,
        )

    with col_b:
        st.plotly_chart(
            chart_energy_pie(
                last_inputs["solar"],
                last_inputs["hydrogen"],
                last_inputs["ess"],
                last_inputs["external"],
            ),
            use_container_width=True,
        )

    with col_c:
        st.plotly_chart(
            chart_need_radar(resource_obj),
            use_container_width=True,
        )

    st.subheader("구역별 상세 결과")

    detail_df = pd.DataFrame(
        {
            "구역": DISTRICT_KEYS,
            "만족도": [result["districts"][k] for k in DISTRICT_KEYS],
            "상태": [score_label(result["districts"][k]) for k in DISTRICT_KEYS],
        }
    )

    st.dataframe(detail_df, use_container_width=True)

# ==================================================
# TAB 2: 에너지 분석
# ==================================================
with tab2:
    st.subheader("에너지 배분 상세 분석")

    st.markdown(
        """
        에너지 배분은 도시의 **에너지 자립률**과 시민 만족도 보정에 영향을 줍니다.  
        외부전력망은 안정적이지만 자립률에는 기여하지 않고, 태양광·수소·ESS는 각기 다른 효율로 자립률에 기여합니다.
        """
    )

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.plotly_chart(
            chart_energy_bar(
                last_inputs["solar"],
                last_inputs["hydrogen"],
                last_inputs["ess"],
                last_inputs["external"],
            ),
            use_container_width=True,
        )

    with col2:
        energy_summary = pd.DataFrame(
            [
                ["태양광", last_inputs["solar"], 0.70, last_inputs["solar"] * 0.70],
                ["수소연료전지", last_inputs["hydrogen"], 0.90, last_inputs["hydrogen"] * 0.90],
                ["ESS", last_inputs["ess"], 0.60, last_inputs["ess"] * 0.60],
                ["외부전력망", last_inputs["external"], 0.00, 0.00],
            ],
            columns=["에너지원", "구성 비율(%)", "자립률 기여계수", "자립률 기여(%p)"],
        )

        st.dataframe(energy_summary, use_container_width=True)

        st.markdown(
            f"""
            <div class="alert-info">
                <b>현재 에너지 자립률</b>: 
                <span style="color:{energy_color};font-weight:800">{energy_rate*100:.1f}%</span><br>
                <b>만족도 보정값</b>: {energy_bonus:+.1f}점<br>
                <b>해석</b>: 에너지 자립률이 높을수록 외부 전력 의존이 줄어들고 도시 안정성이 높아집니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("에너지 자립률 구간 해석")

    interpretation_df = pd.DataFrame(
        [
            ["0% 이상 ~ 40% 미만", "위험", "외부 전력 의존도가 높아 만족도에 패널티가 발생"],
            ["40% 이상 ~ 60% 미만", "불안정", "기본 공급은 가능하지만 안정적 자립에는 부족"],
            ["60% 이상 ~ 80% 미만", "안정", "자립 기반이 형성되어 만족도에 긍정적 보정"],
            ["80% 이상", "자립 우수", "자립형 스마트시티에 가까운 상태"],
        ],
        columns=["자립률 구간", "상태", "해석"],
    )

    st.dataframe(interpretation_df, use_container_width=True)

# ==================================================
# TAB 3: 시나리오 비교
# ==================================================
with tab3:
    st.subheader("프리셋 시나리오 비교")

    compare_results = {}

    for name, preset in PRESETS.items():
        if preset is None:
            continue

        preset_result, _, err = run_simulation(
            preset["welfare"],
            preset["education"],
            preset["energy_infra"],
            preset["general_infra"],
            preset["safety"],
            preset["solar"],
            preset["hydrogen"],
            preset["ess"],
            preset["external"],
        )

        if err is None:
            compare_results[name] = preset_result

    compare_results["현재 입력"] = result

    st.plotly_chart(
        chart_scenario_compare(compare_results),
        use_container_width=True,
    )

    scenario_table = []

    for name, r in compare_results.items():
        scenario_table.append(
            {
                "시나리오": name,
                "도시 평균 만족도": round(r["city_average"], 1),
                "에너지 자립률(%)": round(r["independence_rate"] * 100, 1),
                "최저 구역 만족도": round(min(r["districts"].values()), 1),
                "위험 구역 수": sum(1 for v in r["districts"].values() if v < 50),
            }
        )

    st.dataframe(pd.DataFrame(scenario_table), use_container_width=True)

    st.plotly_chart(
        chart_district_heatmap(compare_results),
        use_container_width=True,
    )

    st.subheader("비선형 예산 효과")

    st.markdown(
        """
        이 시뮬레이터는 예산이 단순히 많이 투입된다고 만족도가 선형적으로 증가한다고 가정하지 않습니다.  
        일정 수준 이하의 투자는 효과가 급격히 낮고, 적정 구간을 넘어서면 한계효용이 체감하도록 설계되어 있습니다.
        """
    )

    st.plotly_chart(chart_nonlinear_curve(), use_container_width=True)

# ==================================================
# TAB 4: 프로젝트 소개
# ==================================================
with tab4:
    st.subheader("프로젝트 문제의식")

    st.markdown(
        """
        이 프로젝트는 스마트시티를 단순히 ICT, AI, 빅데이터 기술을 많이 도입한 도시로 보지 않습니다.  
        오히려 같은 예산과 같은 에너지 자원이 주어졌을 때,  
        **어디에 어떻게 배분하느냐가 시민의 체감 만족도를 결정한다**는 관점에서 출발합니다.

        따라서 NOVA시 시뮬레이터는 다음 질문을 다룹니다.

        1. 복지, 교육, 인프라, 안전, 에너지 인프라 중 무엇을 우선할 것인가?
        2. 태양광, 수소, ESS, 외부전력망 중 어떤 에너지 구성을 선택할 것인가?
        3. 그 선택은 구역별 시민 만족도와 에너지 자립률을 어떻게 바꾸는가?
        4. 전체 평균이 높아지더라도 특정 구역이 소외되는 트레이드오프는 없는가?
        """
    )

    st.subheader("시민 유형과 구역 설정")

    citizen_df = pd.DataFrame(
        [
            ["근로자", "모빌리티 + 기회", "출퇴근과 일자리 기회에 민감"],
            ["학생", "기회 + 활동", "교육·취업·문화 인프라에 민감"],
            ["돌봄담당자", "건강·안전 + 거버넌스", "보육·복지 정책에 민감"],
            ["실업자", "기회 + 거버넌스", "취업 지원과 정책 접근성에 민감"],
            ["노인", "건강·안전 + 모빌리티", "의료 접근성과 이동권에 민감"],
        ],
        columns=["시민 유형", "핵심 니즈", "설명"],
    )

    st.dataframe(citizen_df, use_container_width=True)

    district_df = pd.DataFrame(
        [
            ["A구역", "산업단지", "근로자 중심"],
            ["B구역", "대학가", "학생 중심"],
            ["C구역", "복지타운", "노인 중심"],
            ["D구역", "신도시", "혼합 구성"],
            ["E구역", "구도심", "혼합 구성 + 취약성"],
        ],
        columns=["구역", "성격", "주요 시민 구성"],
    )

    st.dataframe(district_df, use_container_width=True)

    st.info(
        "이 대시보드는 실제 도시 데이터를 그대로 예측하는 모델이라기보다, "
        "스마트시티 정책에서 예산 배분과 에너지 구성이 만드는 트레이드오프를 설명하기 위한 OOP 기반 정책 시뮬레이터입니다."
    )
