import streamlit as st
import pandas as pd

# Настройки страницы
st.set_page_config(
    page_title="Калькулятор прайса 2026",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Финансовый калькулятор цен и наценок")
st.markdown("Расчет отпускной цены, наценок дистрибьютора, сетей и цены на полке.")

st.divider()

# Боковая панель ввода
st.sidebar.header("⚙️ Параметры расчета")

brand = st.sidebar.text_input("Торговая марка", value="Новый бренд 2026")
base_price = st.sidebar.number_input("Базовая цена (руб/бут)", min_value=0.0, value=590.0, step=10.0)
lmb_percent = st.sidebar.number_input("ЛМБ (%)", min_value=0.0, value=8.0, step=0.5)

# Логика расчетов
lmb_rub = round(base_price * (lmb_percent / 100))
distributor_in = base_price + lmb_rub
min_price = round(distributor_in * 1.25)        # +25%
regional_nets_in = round(distributor_in * 1.35) # +35%
shelf_price = round(regional_nets_in * 1.3837)  # Рекомендуемая полка

# Вывод ключевых метрик
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("ЛМБ (руб)", f"{lmb_rub:,.0f} ₽".replace(",", " "))
col2.metric("Вход ДИСТРИБЬЮТОР", f"{distributor_in:,.0f} ₽".replace(",", " "))
col3.metric("Min Price (+25%)", f"{min_price:,.0f} ₽".replace(",", " "))
col4.metric("Вход РЕГ. СЕТИ (+35%)", f"{regional_nets_in:,.0f} ₽".replace(",", " "))
col5.metric("Цена на полке", f"{shelf_price:,.0f} ₽".replace(",", " "))

st.divider()

# Итоговая таблица
st.subheader("📊 Сводная таблица")

df_result = pd.DataFrame([{
    "Торговая марка": brand,
    "Базовая цена": f"{base_price:,.0f} ₽".replace(",", " "),
    "ЛМБ": f"{lmb_rub:,.0f} ₽ ({lmb_percent}%)".replace(",", " "),
    "Вход Дистрибьютор": f"{distributor_in:,.0f} ₽".replace(",", " "),
    "Min Price": f"{min_price:,.0f} ₽".replace(",", " "),
    "Вход Рег. Сети": f"{regional_nets_in:,.0f} ₽".replace(",", " "),
    "Цена на полке": f"{shelf_price:,.0f} ₽".replace(",", " ")
}])

st.dataframe(df_result, hide_index=True, use_container_width=True)

st.caption("* Цены указаны самовывозом со склада. Все цены включают НДС.")