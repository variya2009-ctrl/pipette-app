import streamlit as st
import numpy as np

# Настройка страницы в лабораторном стиле
st.set_page_config(page_title="Виртуальный колориметр", page_icon="🧪", layout="wide")

# Кастомный CSS для шрифта и красивого отображения цветных плашек
st.markdown("""
    <style>
    /* Применяем шрифт Arial Black / Impact к главным заголовкам для стильного вида */
    h1, h2, h3 {
        font-family: 'Arial Black', 'Impact', sans-serif !important;
        letter-spacing: 0.5px;
    }
    /* Стиль для цветных плашек-превью */
    .color-box {
        width: 100%;
        height: 38px;
        border-radius: 8px;
        border: 2px solid #ccc;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
    }
    /* Смещение превью чуть ниже, чтобы выровнять с полями ввода */
    .color-container {
        padding-top: 28px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🧪 ВИРТУАЛЬНЫЙ КОЛОРИМЕТР ")
st.caption("Лабораторный экспресс-анализ концентрации растворов по оптическим координатам RGB")
st.write("---")

# Инициализация состояния для дополнительных строк
if "extra_rows" not in st.session_state:
    st.session_state.extra_rows = 0

# Функция расчета
def calculate_concentration(known_data, target_rgb):
    # Разделяем входные данные на цвета и концентрации отдельно
    known_rgb = np.array([item[:3] for item in known_data], dtype=float)
    known_c = np.array([item[3] for item in known_data], dtype=float)
    target_rgb = np.array(target_rgb, dtype=float)
    
    # 1. Вычисления: Метод Евклидова расстояния
    distances = np.linalg.norm(known_rgb - target_rgb, axis=1)
    weights = 1.0 / (distances + 1e-6)
    weights /= np.sum(weights)
    c_predicted_euclidean = np.sum(weights * known_c)
    
    # 2. Вычисления: Закон Бугера-Ламберта-Бера
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
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("## 📌 ИЗВЕСТНЫЕ РАСТВОРЫ")
    known_inputs = []
    
    # --- СТРОКА 1: МАКСИМУМ ---
    with st.expander("📈 РАСТВОР МАКСИМАЛЬНОЙ КОНЦЕНТРАЦИИ", expanded=True):
        c_max_cols = st.columns(5)
        with c_max_cols[0]: max_r = st.number_input("R", min_value=0, max_value=255, value=50, key="max_r")
        with c_max_cols[1]: max_g = st.number_input("G", min_value=0, max_value=255, value=20, key="max_g")
        with c_max_cols[2]: max_b = st.number_input("B", min_value=0, max_value=255, value=10, key="max_b")
        with c_max_cols[3]: max_c = st.number_input("Концентрация", value=16.0, key="max_c")
        with c_max_cols[4]:
            st.markdown('<div class="color-container"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="color-box" style="background-color: rgb({max_r},{max_g},{max_b});"></div>', unsafe_allow_html=True)
        known_inputs.append([max_r, max_g, max_b, max_c])
    
    # --- СТРОКА 2: МИНИМУМ ---
    with st.expander("📉 РАСТВОР МИНИМАЛЬНОЙ КОНЦЕНТРАЦИИ", expanded=True):
        c_min_cols = st.columns(5)
        with c_min_cols[0]: min_r = st.number_input("R", min_value=0, max_value=255, value=200, key="min_r")
        with c_min_cols[1]: min_g = st.number_input("G", min_value=0, max_value=255, value=220, key="min_g")
        with c_min_cols[2]: min_b = st.number_input("B", min_value=0, max_value=255, value=240, key="min_b")
        with c_min_cols[3]: min_c = st.number_input("Концентрация", value=1.0, key="min_c")
        with c_min_cols[4]:
            st.markdown('<div class="color-container"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="color-box" style="background-color: rgb({min_r},{min_g},{min_b});"></div>', unsafe_allow_html=True)
        known_inputs.append([min_r, min_g, min_b, min_c])
    
    # --- ДИНАМИЧЕСКИЕ СТРОКИ ---
    for i in range(st.session_state.extra_rows):
        with st.expander(f" ПРОМЕЖУТОЧНЫЙ РАСТВОР #{i+1}", expanded=True):
            c_cols = st.columns(5)
            with c_cols[0]: dr = st.number_input("R", min_value=0, max_value=255, value=100, key=f"dr_{i}")
            with c_cols[1]: dg = st.number_input("G", min_value=0, max_value=255, value=100, key=f"dg_{i}")
            with c_cols[2]: db = st.number_input("B", min_value=0, max_value=255, value=100, key=f"db_{i}")
            with c_cols[3]: dc = st.number_input("Концентрация", value=5.0, key=f"dc_{i}")
            with c_cols[4]:
                st.markdown('<div class="color-container"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="color-box" style="background-color: rgb({dr},{dg},{db});"></div>', unsafe_allow_html=True)
            known_inputs.append([dr, dg, db, dc])
        
    if st.button("➕ ДОБАВИТЬ ТОЧКУ КАЛИБРОВКИ", use_container_width=True):
        st.session_state.extra_rows += 1
        st.rerun()
        
    st.write("---")
    
    # --- ТЕСТИРУЕМЫЙ ОБРАЗЕЦ ---
    st.markdown("##  ТЕСТИРУЕМЫЙ ОБРАЗЕЦ")
    with st.expander(" НЕИЗВЕСТНЫЙ РАСТВОР (ЦЕЛЬ)", expanded=True):
        c_target_cols = st.columns(5)
        with c_target_cols[0]: target_r = st.number_input("R", min_value=0, max_value=255, value=120, key="t_r")
        with c_target_cols[1]: target_g = st.number_input("G", min_value=0, max_value=255, value=110, key="t_g")
        with c_target_cols[2]: target_b = st.number_input("B", min_value=0, max_value=255, value=115, key="t_b")
        with c_target_cols[3]: 
            st.markdown('<div class="color-container"></div>', unsafe_allow_html=True)
            st.caption("🔍 Ищем конц.")
        with c_target_cols[4]:
            st.markdown('<div class="color-container"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="color-box" style="background-color: rgb({target_r},{target_g},{target_b});"></div>', unsafe_allow_html=True)

with col2:
    st.markdown("## 📊 РЕЗУЛЬТАТЫ ЭКСПРЕСС-АНАЛИЗА")
    st.info("ℹ️ Нажмите кнопку ниже, чтобы запустить математические модели.")
    
    if st.button("🚀 НАЧАТЬ РАСЧЁТ КОНЦЕНТРАЦИИ", type="primary", use_container_width=True):
        target_rgb = [target_r, target_g, target_b]
        euclid, beer, points = calculate_concentration(known_inputs, target_rgb)
        
        # Крупные карточки с результатами (без цветовой индикации и стрелочек)
        st.metric(
            label="🎯 СПОСОБ 1: МАТРИЦА ЕВКЛИДОВЫХ РАССТОЯНИЙ (RGB)", 
            value=f"{euclid:.2f}"
        )
        st.markdown("> **Как это посчитано:** Модель ищет геометрическое сходство цветового вектора в трёхмерном пространстве RGB относительно калибровочных пробирок.")
        
        st.write("")
        st.metric(
            label="📉 СПОСОБ 2: ЗАКОН БУГЕРА-ЛАМБЕРТА-ВЕРА (СПЕКТР)", 
            value=f"{beer:.2f}"
        )
        st.markdown("> **Как это посчитано:** Модель переводит RGB в физическую величину абсорбции (поглощения света). Это стандарт аналитической химии.")
        
        st.info(f"Анализ завершен. Использовано {points} опорных калибровочных растворов.")
