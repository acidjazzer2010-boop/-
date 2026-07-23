import streamlit as st
import pandas as pd
import io

# Настройки страницы
st.set_page_config(
    page_title="Прайс КРАЙВИН 2026",
    page_icon="🍷",
    layout="wide"
)

st.title("🍷 Прайс-Калькулятор КРАЙВИН 2026")
st.caption("Расчет цен для клиентов, минимальной цены и цены на полке (без ЛМБ)")

st.divider()

# Переключатель режимов
app_mode = st.radio(
    "Выберите режим работы:",
    ["🧮 Интерактивный калькулятор", "📁 Расчет из файла Excel"],
    horizontal=True
)

st.divider()

# Боковая панель с процентами наценок по умолчанию
st.sidebar.header("⚙️ Проценты наценок")
default_markup_buy = st.sidebar.number_input("Наценка на закупку (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.5)
default_markup_tk = st.sidebar.number_input("Наценка на подвоз до ТК (%)", min_value=0.0, max_value=50.0, value=5.0, step=1.0)


# --- 1. ИНТЕРАКТИВНЫЙ КАЛЬКУЛЯТОР ---
if app_mode == "🧮 Интерактивный калькулятор":

    st.subheader("1. Параметры позиции")

    col1, col2 = st.columns(2)

    with col1:
        series_name = st.text_input("Серия / Торговая марка", value="Мезенка 25")
        year_val = st.number_input("ГОД", min_value=2024, max_value=2030, value=2025)
        price_discount = st.number_input("Цена со скидкой (руб/бут)", min_value=1.0, value=650.0, step=10.0)

    with col2:
        markup_buy = st.number_input("Наценка на закупку (%)", min_value=0.0, value=default_markup_buy, step=0.5) / 100.0
        markup_tk = st.number_input("Наценка на подвоз до ТК (%)", min_value=0.0, value=default_markup_tk, step=1.0) / 100.0
        shelf_price = st.number_input("Рекомендуемая цена на полке (руб/бут)", min_value=1.0, value=1300.0, step=10.0)

    # Расчеты
    kravin_in = price_discount
    moscow_price = round(kravin_in * (1.0 + markup_buy), 2)
    min_price = round(moscow_price * (1.0 + markup_tk), 2)
    shelf_markup_pct = round(((shelf_price - min_price) / min_price) * 100.0, 1) if min_price > 0 else 0.0

    st.divider()
    st.subheader("2. Результаты ценовой цепочки")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Вход КРАЙВИН", f"{kravin_in:,.0f} ₽".replace(",", " "))
    m2.metric("Цена из Москвы", f"{moscow_price:,.2f} ₽".replace(",", " "), delta=f"+{markup_buy*100:.1f}%")
    m3.metric("Минимальная цена", f"{min_price:,.2f} ₽".replace(",", " "), delta=f"+{markup_tk*100:.1f}%")
    m4.metric("Цена на полке", f"{shelf_price:,.0f} ₽".replace(",", " "))
    m5.metric("% наценки от мин. цены", f"{shelf_markup_pct}%")

    st.subheader("3. Сводная таблица")
    df_single = pd.DataFrame([{
        "Серия": series_name,
        "ГОД": year_val,
        "Цена со скидкой 10%": price_discount,
        "Входная цена КРАЙВИН": kravin_in,
        "Наценка на закупку": f"{markup_buy*100:.1f}%",
        "Цена из Москвы для клиентов": moscow_price,
        "Наценка на подвоз до ТК": f"{markup_tk*100:.1f}%",
        "Минимальная цена": min_price,
        "Рекомендуемая цена на полке": shelf_price,
        "% наценки от мин. цены": f"{shelf_markup_pct}%"
    }])

    st.dataframe(df_single, hide_index=True, use_container_width=True)


# --- 2. РАСЧЕТ ИЗ ФАЙЛА EXCEL ---
else:
    st.subheader("📁 Автоматический расчет из Excel")
    uploaded_file = st.file_uploader("Загрузить файл Excel (.xlsx)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df_raw = pd.read_excel(uploaded_file, header=1) # Берем заголовки из 2-й строки
            st.success("Файл успешно загружен!")

            results = []
            for idx, row in df_raw.iterrows():
                series = row.get("Серия", row.iloc[1] if len(row) > 1 else f"Товар {idx+1}")
                if pd.isna(series) or str(series).startswith("Цена включает") or str(series).startswith("*"):
                    continue

                year = row.get("ГОД", 2025)
                price_disc = float(row.get("Цена со скидкой 10% на 2024 г.", row.iloc[3] if len(row) > 3 else 0))
                
                if price_disc > 0:
                    m_buy = float(row.get("Наценка на закупку", default_markup_buy / 100.0))
                    m_tk = float(row.get("Наценка на подвоз до ТК", default_markup_tk / 100.0))
                    shelf = float(row.get("Рекомендуемая цена на полке", row.iloc[8] if len(row) > 8 else 0))

                    k_in = price_disc
                    p_moscow = round(k_in * (1.0 + m_buy), 2)
                    p_min = round(p_moscow * (1.0 + m_tk), 2)
                    pct_shelf = round(((shelf - p_min) / p_min) * 100.0, 1) if p_min > 0 else 0.0

                    results.append({
                        "Серия": series,
                        "ГОД": year,
                        "Цена со скидкой 10%": price_disc,
                        "Входная цена КРАЙВИН (руб/бут)": k_in,
                        "Наценка на закупку": m_buy,
                        "Цена из Москвы для клиентов (кроме ЮФО) (руб/бут)": p_moscow,
                        "Наценка на подвоз до ТК": m_tk,
                        "Минимальная цена (руб/бут)": p_min,
                        "Рекомендуемая цена на полке": shelf,
                        "% наценки от минимальной цены": f"{pct_shelf}%"
                    })

            if results:
                df_res = pd.DataFrame(results)
                st.dataframe(df_res, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Прайс 2026')

                st.download_button(
                    label="📥 Скачать пересчитанный Прайс в Excel",
                    data=buffer.getvalue(),
                    file_name="Прайс_КРАЙВИН_2026.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")
