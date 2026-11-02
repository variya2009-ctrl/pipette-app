import streamlit as st
import numpy as np

# Настройка страницы
st.set_page_config(page_title="Виртуальный Колориметр", page_icon="🧪", layout="wide")

st.title("🧪 Виртуальный Колориметр (Умная Пипетка)")
st.write("Введите RGB-значения и известные концентрации для калибровки метода.")

# Инициализация состояния для дополнительных строк
if "extra_rows" not in st.session_state:
    st.session_state.extra_rows = 0

# Функция расчета
def calculate_concentration(known_data, target_rgb):
    known_rgb = np.array([item[:3] for item in known_data])
    known_c = np.array([item[3] for item in known_data])
    target_rgb = np.array(target_rgb)
    
    # Вычисления: Метод Евклидова расстояния
    distances = np.linalg.norm(known_rgb - target_rgb, axis=1)
    weights = 1.0 / (distances + 1e-6)
    weights /= np.sum(weights)
    c_predicted_euclidean = np.sum(weights * known_c)
    
    # Вычисления: Закон Бугера-Ламберта-Бера
    intensities = np.clip(known_rgb, 1, 255)
    absorbance_known = -np.log(intensities / 255.0)
    abs_mean_known = absorbance_known.mean(axis=1)
    
    target_intensity = np.clip(target_rgb, 1, 255)
    target_abs = (-np.log(target_intensity / 255.0)).mean()
    
    k_coefficients = abs_mean_known / known_c
    k_mean = np.mean(k_coefficients)
    c_predicted_beer = target_abs / k_mean if k_mean != 0 else 0.0
    
    return max(0.0, c_predicted_euclidean), max(0.0, c_predicted_beer), len(known_c)

# Верстка интерфейса
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Известные растворы")
    
    known_inputs = []
    
    # Базовая строка 1: Максимум
    st.markdown("**Макс. конц.**")
    c_max_cols = st.columns(4)
    with c_max_cols[0]: max_r = st.number_input("R", min_value=0, max_value=255, value=50, key="max_r")
    with c_max_cols[1]: max_g = st.number_input("G", min_value=0, max_value=255, value=20, key="max_g")
    with c_max_cols[2]: max_b = st.number_input("B", min_value=0, max_value=255, value=10, key="max_b")
    with c_max_cols[3]: max_c = st.number_input("Концентрация", value=10.0, key="max_c")
    known_inputs.append([max_r, max_g, max_b, max_c])
    
    # Базовая строка 2: Минимум
    st.markdown("**Мин. конц.**")
    c_min_cols = st.columns(4)
    with c_min_cols[0]: min_r = st.number_input("R", min_value=0, max_value=255, value=200, key="min_r")
    with c_min_cols[1]: min_g = st.number_input("G", min_value=0, max_value=255, value=220, key="min_g")
    with c_min_cols[2]: min_b = st.number_input("B", min_value=0, max_value=255, value=240, key="min_b")
    with c_min_cols[3]: min_c = st.number_input("Концентрация", value=1.0, key="min_c")
    known_inputs.append([min_r, min_g, min_b, min_c])
    
    # Динамические строки
    for i in range(st.session_state.extra_rows):
        st.markdown(f"**Раствор #{i+1}**")
        c_cols = st.columns(4)
        with c_cols[0]: dr = st.number_input("R", min_value=0, max_value=255, value=100, key=f"dr_{i}")
        with c_cols[1]: dg = st.number_input("G", min_value=0, max_value=255, value=100, key=f"dg_{i}")
        with c_cols[2]: db = st.number_input("B", min_value=0, max_value=255, value=100, key=f"db_{i}")
        with c_cols[3]: dc = st.number_input("Концентрация", value=5.0, key=f"dc_{i}")
        known_inputs.append([dr, dg, db, dc])
        
    if st.button("➕ Добавить строку калибровки"):
        st.session_state.extra_rows += 1
        st.rerun()
        
    st.subheader("🔍 Неизвестный раствор")
    c_target_cols = st.columns(3)
    with c_target_cols[0]: target_r = st.number_input("R", min_value=0, max_value=255, value=120, key="t_r")
    with c_target_cols[1]: target_g = st.number_input("G", min_value=0, max_value=255, value=110, key="t_g")
    with c_target_cols[2]: target_b = st.number_input("B", min_value=0, max_value=255, value=115, key="t_b")

with col2:
    st.subheader("📈 Вывод результатов")
    if st.button("🚀 Рассчитать", type="primary"):
        target_rgb = [target_r, target_g, target_b]
        euclid, beer, points = calculate_concentration(known_inputs, target_rgb)
        
        st.success("Успешно рассчитано!")
        st.metric(label="Способ 1: Евклидово расстояние (RGB)", value=f"{euclid:.4f}")
        st.metric(label="Способ 2: Закон Бугера-Ламберта-Бера", value=f"{beer:.4f}")
        st.caption(f"Использовано калибровочных точек: {points}")
