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
""", unsafe_allow_allow_html=True)

st.markdown('<div class="main-title">🍷 Прайс-Калькулятор 2026 (Дистрибьюция и Сети)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Расчет входных цен дистрибьюторов, региональных сетей, наценок и цены на полке</div>', unsafe_allow_html=True)

# Navigation / Mode Selection
app_mode = st.sidebar.radio("Выберите режим работы:", ["🧮 Интерактивный калькулятор", "📁 Загрузка и расчет файла Excel"])

st.sidebar.divider()
st.sidebar.header("⚙️ Глобальные наценки и коэффициенты")

# Customizable percentage parameters
lmb_pct = st.sidebar.number_input("Ставка ЛМБ (%)", min_value=0.0, max_value=50.0, value=8.0, step=0.5, help="Процент маркетиногового бонуса / ЛМБ от базы")
dist_markup_pct = st.sidebar.number_input("Наценка Дистрибьютора / Min Price (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0, help="Наценка дистрибьютора на входную цену")
net_markup_pct = st.sidebar.number_input("Наценка Региональных Сетей (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0, help="Наценка сетей на цену дистрибьютора")
shelf_markup_pct = st.sidebar.number_input("Наценка полки / Ритейла (%)", min_value=0.0, max_value=200.0, value=38.4, step=0.5, help="Наценка магазина от цены рег. сетей до полки")

# --- MODE 1: INTERACTIVE CALCULATOR ---
if app_mode == "🧮 Интерактивный калькулятор":
    
    st.subheader("1. Параметры товара и направление расчета")
    
    calc_type = st.radio(
        "Направление расчета:",
        ["Прямой расчет (от Базовой цены ➔ к Полке)", "Обратный расчет (от Цены на полке ➔ к Базовой цене)"],
        horizontal=True
    )
    
    col_in1, col_in2 = st.columns([2, 2])
    
    with col_in1:
        brand_name = st.text_input("Торговая марка / SKU", value="Мезенка 25")
        year_val = st.number_input("Год", min_value=2024, max_value=2030, value=2025)

    with col_in2:
        if "Прямой" in calc_type:
            base_input = st.number_input("Базовая цена (руб/бут)", min_value=1.0, value=650.0, step=10.0)
            
            # Direct Calculations
            lmb_val = round(base_input * (lmb_pct / 100.0))
            dist_in = base_input + lmb_val
            min_p = round(dist_in * (1.0 + dist_markup_pct / 100.0))
            reg_in = round(dist_in * (1.0 + net_markup_pct / 100.0))
            shelf_p = round(reg_in * (1.0 + shelf_markup_pct / 100.0))
            
        else:
            shelf_input = st.number_input("Желаемая цена на полке (руб/бут)", min_value=1.0, value=1300.0, step=10.0)
            
            # Reverse Calculations
            reg_in = round(shelf_input / (1.0 + shelf_markup_pct / 100.0))
            dist_in = round(reg_in / (1.0 + net_markup_pct / 100.0))
            min_p = round(dist_in * (1.0 + dist_markup_pct / 100.0))
            base_input = round(dist_in / (1.0 + lmb_pct / 100.0))
            lmb_val = dist_in - base_input
            shelf_p = shelf_input

    st.divider()
    st.subheader("2. Результаты расчета ценовой цепочки")
    
    # Display metrics in cards
    m1, m2, m3, m4, m5 = st.columns(5)
    
    m1.metric("БАЗА", f"{base_input:,.0f} ₽".replace(",", " "))
    m2.metric("ЛМБ", f"{lmb_val:,.0f} ₽".replace(",", " "), delta=f"+{lmb_pct}%")
    m3.metric("Вход ДИСТРИБЬЮТОР", f"{dist_in:,.0f} ₽".replace(",", " "))
    m4.metric("Вход РЕГ. СЕТИ", f"{reg_in:,.0f} ₽".replace(",", " "), delta=f"+{net_markup_pct}%")
    m5.metric("Цена на полке", f"{shelf_p:,.0f} ₽".replace(",", " "), delta=f"+{shelf_markup_pct}%")

    st.markdown("---")
    
    # Secondary Info Cards
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"📌 **«Min price» (дистрибьютор +{dist_markup_pct}%):** **{min_p:,.0f} ₽**".replace(",", " "))
    with c2:
        total_markup = ((shelf_p - dist_in) / dist_in * 100) if dist_in > 0 else 0
        st.success(f"📈 **Сквозная наценка (от входа дистрибьютора до полки):** **{total_markup:.1f}%**")

    # Detailed Table
    st.subheader("3. Сводная таблица по позиции")
    df_single = pd.DataFrame([{
        "Торговая марка": brand_name,
        "Год": year_val,
        "БАЗА (руб)": base_input,
        f"ЛМБ руб ({lmb_pct:.0f}%)": lmb_val,
        "Вход ДИСТРИБЬЮТОР (руб)": dist_in,
        "«Min price» (руб)": min_p,
        "Вход РЕГИОНАЛЬНЫЕ СЕТИ (руб)": reg_in,
        "Рекомендуемая цена на полке (руб)": shelf_p
    }])
    
    st.dataframe(df_single, hide_index=True, use_container_width=True)

# --- MODE 2: EXCEL FILE PROCESSING ---
else:
    st.subheader("📁 Автоматический расчет прайс-листа из файла Excel")
    st.write("Загрузите ваш файл Excel (например, `ФИН_Прайс_2026 Дистрибьюторы_2.xlsx`) для автоматического пересчета всех позиций.")

    uploaded_file = st.file_uploader("Загрузить файл Excel (.xlsx)", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Read excel
            df_raw = pd.read_excel(uploaded_file)
            st.success("Файл успешно загружен!")
            
            with st.expander("Просмотр исходных данных из файла"):
                st.dataframe(df_raw)
            
            # Auto-detect or recalculate rows
            st.subheader("📊 Пересчитанные данные по текущим формулам")
            
            # Search for base price column or brand column
            # Process table
            results = []
            
            # Simple column matching logic
            for idx, row in df_raw.iterrows():
                row_str = " ".join([str(v) for v in row.values if pd.notna(v)])
                
                # Check numeric base value in row
                numbers = [v for v in row.values if isinstance(v, (int, float)) and not pd.isna(v)]
                
                if len(numbers) >= 1:
                    # Brand name from first text cell
                    text_cells = [str(v) for v in row.values if isinstance(v, str) and not pd.isna(v)]
                    brand = text_cells[0] if text_cells else f"Товар {idx+1}"
                    
                    base = float(numbers[0]) if len(numbers) > 0 else 500.0
                    
                    # Calculate
                    lmb_v = round(base * (lmb_pct / 100.0))
                    d_in = base + lmb_v
                    m_p = round(d_in * (1.0 + dist_markup_pct / 100.0))
                    r_in = round(d_in * (1.0 + net_markup_pct / 100.0))
                    s_p = round(r_in * (1.0 + shelf_markup_pct / 100.0))
                    
                    results.append({
                        "Торговая марка": brand,
                        "БАЗА": base,
                        f"ЛМБ ({lmb_pct:.0f}%)": lmb_v,
                        "Вход ДИСТРИБЬЮТОР": d_in,
                        "Min price": m_p,
                        "Вход РЕГ. СЕТИ": r_in,
                        "Цена на полке": s_p
                    })
            
            if results:
                df_calc_result = pd.DataFrame(results)
                st.dataframe(df_calc_result, use_container_width=True)
                
                # Excel Export Button
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_calc_result.to_excel(writer, index=False, sheet_name='Прайс 2026')
                
                st.download_button(
                    label="📥 Скачать пересчитанный Прайс в Excel",
                    data=buffer.getvalue(),
                    file_name="Пересчитанный_Прайс_2026.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Не удалось распознать структуры таблиц. Убедитесь, что в файле есть числовые столбцы с базовыми ценами.")
                
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")

st.sidebar.caption("Все цены рассчитываются с учетом НДС. Условия поставки: самовывоз со склада.")
