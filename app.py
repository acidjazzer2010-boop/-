import streamlit as st
import pandas as pd
import io

# Page Configuration
st.set_page_config(
    page_title="Гибкий Прайс-Калькулятор 2026",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2563EB;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🍷 Прайс-Калькулятор 2026 (Дистрибьюция и Сети)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Расчет входных цен дистрибьюторов, региональных сетей, наценок и цены на полке</div>', unsafe_allow_html=True)
