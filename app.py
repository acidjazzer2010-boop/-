import streamlit as st
import pandas as pd
import io

# Настройки страницы
st.set_page_config(
    page_title="Прайс-Калькулятор 2026",
    page_icon="🍷",
    layout="wide"
)

# Заголовок
st.title("🍷 Прайс-Калькулятор 2026")
st.caption("Расчет входных цен дистрибьюторов, региональных сетей, наценок и цены на полке")

st.divider()

# Переключатель режимов
app_mode = st.radio(
    "Выберите режим работы:",
    ["🧮 Интерактивный калькулятор", "📁 Расчет из файла Excel"],
    horizontal=True
)

st.divider()

# Боковая панель параметров
st.sidebar.header("⚙️ Настройки наценок (%)")
lmb_pct = st.sidebar.number_input("Ставка ЛМБ (%)", min_value=0.0, max_value=50.0, value=8.0, step=0.5)
dist_markup_pct = st.sidebar.number_input("Min Price / Дистрибьютор (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0)
net_markup_pct = st.sidebar.number_input("Региональные Сети (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0)
shelf_markup_pct = st.sidebar.number_input("Наценка полки (%)", min_value=0.0, max_value=200.0, value=38.4, step=0.5)


# --- 1. ИНТЕРАКТИВНЫЙ КАЛЬКУЛЯТОР ---
if app_mode == "🧮 Интерактивный калькулятор":

    st.subheader("1. Параметры товара")

    col_calc_type, col_dummy = st.columns([2, 1])
    with col_calc_type:
        calc_direction = st.radio(
            "Направление расчета:",
            ["Прямой (от Базовой цены → к Полке)", "Обратный (от Полки → к Базовой цене)"],
            horizontal=True
        )

    col1, col2 = st.columns(2)

    with col1:
        brand_name = st.text_input("Торговая марка / SKU", value="Мезенка 25")
        year_val = st.number_input("Год", min_value=2024, max_value=2030, value=2025)

    with col2:
        if "Прямой" in calc_direction:
            base_input = st.number_input("Базовая цена (руб/бут)", min_value=1.0, value=650.0, step=10.0)
            lmb_val = round(base_input * (lmb_pct / 100.0))
            dist_in = base_input + lmb_val
            min_p = round(dist_in * (1.0 + dist_markup_pct / 100.0))
            reg_in = round(dist_in * (1.0 + net_markup_pct / 100.0))
            shelf_p = round(reg_in * (1.0 + shelf_markup_pct / 100.0))
        else:
            shelf_input = st.number_input("Желаемая цена на полке (руб/бут)", min_value=1.0, value=1300.0, step=10.0)
            shelf_p = shelf_input
            reg_in = round(shelf_p / (1.0 + shelf_markup_pct / 100.0))
            dist_in = round(reg_in / (1.0 + net_markup_pct / 100.0))
            min_p = round(dist_in * (1.0 + dist_markup_pct / 100.0))
            base_input = round(dist_in / (1.0 + lmb_pct / 100.0))
            lmb_val = dist_in - base_input

    st.divider()
    st.subheader("2. Результаты ценовой цепочки")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("БАЗА", f"{base_input:,.0f} ₽".replace(",", " "))
    m2.metric("ЛМБ", f"{lmb_val:,.0f} ₽".replace(",", " "), delta=f"+{lmb_pct}%")
    m3.metric("Вход ДИСТРИБЬЮТОР", f"{dist_in:,.0f} ₽".replace(",", " "))
    m4.metric("Вход РЕГ. СЕТИ", f"{reg_in:,.0f} ₽".replace(",", " "), delta=f"+{net_markup_pct}%")
    m5.metric("Цена на полке", f"{shelf_p:,.0f} ₽".replace(",", " "), delta=f"+{shelf_markup_pct}%")

    st.info(f"💡 **«Min price» (дистрибьютор +{dist_markup_pct}%):** {min_p:,.0f} ₽".replace(",", " "))

    st.subheader("3. Таблица для копирования")
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


# --- 2. РАСЧЕТ ИЗ ФАЙЛА EXCEL ---
else:
    st.subheader("📁 Автоматический расчет из Excel")
    uploaded_file = st.file_uploader("Загрузить файл Excel (.xlsx)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df_raw = pd.read_excel(uploaded_file)
            st.success("Файл успешно загружен!")

            results = []
            for idx, row in df_raw.iterrows():
                numbers = [v for v in row.values if isinstance(v, (int, float)) and not pd.isna(v)]
                text_cells = [str(v) for v in row.values if isinstance(v, str) and not pd.isna(v)]

                if len(numbers) >= 1:
                    brand = text_cells[0] if text_cells else f"Товар {idx+1}"
                    base = float(numbers[0])

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
                df_res = pd.DataFrame(results)
                st.dataframe(df_res, use_container_width=True)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_res.to_excel(writer, index=False, sheet_name='Прайс')

                st.download_button(
                    label="📥 Скачать пересчитанный Прайс в Excel",
                    data=buffer.getvalue(),
                    file_name="Рассчитанный_Прайс_2026.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")
