import streamlit as st
import numpy as np

# Настройка страницы в лабораторном стиле
st.set_page_config(page_title="Умная Пипетка", page_icon="🧪", layout="wide")

# Подключаем шрифт Impact для заголовков через кастомный CSS
st.markdown("""
    <style>
    /* Применяем шрифт Impact к главным заголовкам */
    h1, h2, h3 {
        font-family: 'Impact', 'Arial Black', sans-serif !important;
        letter-spacing: 1px;
    }
    /* Делаем эмодзи чуть крупнее и красивее */
    .emoji-style {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🧪 ВИРТУАЛЬНЫЙ КОЛОРИМЕТР (УМНАЯ ПИПЕТКА)")
st.caption("📱 Лабораторный экспресс-анализ концентрации растворов по оптическим координатам RGB")
st.write("---")

# Инициализация состояния для дополнительных строк
if "extra_rows" not in st.session_state:
    st.session_state.extra_rows = 0

# Функция расчета
def calculate_concentration(known_data, target_rgb):
    known_rgb = np.array([item[:3] for item in known_data])
    known_c = np.array([item for item in known_data])
    target_rgb = np.array(target_rgb)
    
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
    st.markdown("## 🟢 ИЗВЕСТНЫЕ РАСТВОРЫ")
    known_inputs = []
    
    # --- СТРОКА 1: МАКСИМУМ ---
    with st.expander("📈 РАСТВОР МАКСИМАЛЬНОЙ КОНЦЕНТРАЦИИ", expanded=True):
        c_max_cols = st.columns(4)
        with c_max_cols[0]: max_r = st.number_input("R", min_value=0, max_value=255, value=50, key="max_r")
        with c_max_cols[1]: max_g = st.number_input("G", min_value=0, max_value=255, value=20, key="max_g")
        with c_max_cols[2]: max_b = st.number_input("B", min_value=0, max_value=255, value=10, key="max_b")
        with c_max_cols[3]: max_c = st.number_input("Концентрация", value=16.0, key="max_c")
        known_inputs.append([max_r, max_g, max_b, max_c])
    
    # --- СТРОКА 2: МИНИМУМ ---
    with st.expander("📉 РАСТВОР МИНИМАЛЬНОЙ КОНЦЕНТРАЦИИ", expanded=True):
        c_min_cols = st.columns(4)
        with c_min_cols[0]: min_r = st.number_input("R", min_value=0, max_value=255, value=200, key="min_r")
        with c_min_cols[1]: min_g = st.number_input("G", min_value=0, max_value=255, value=220, key="min_g")
        with c_min_cols[2]: min_b = st.number_input("B", min_value=0, max_value=255, value=240, key="min_b")
        with c_min_cols[3]: min_c = st.number_input("Концентрация", value=1.0, key="min_c")
        known_inputs.append([min_r, min_g, min_b, min_c])
    
    # --- ДИНАМИЧЕСКИЕ СТРОКИ ---
    for i in range(st.session_state.extra_rows):
        with st.expander(f"🧪 ПРОМЕЖУТОЧНЫЙ РАСТВОР #{i+1}", expanded=True):
            c_cols = st.columns(4)
            with c_cols[0]: dr = st.number_input("R", min_value=0, max_value=255, value=100, key=f"dr_{i}")
            with c_cols[1]: dg = st.number_input("G", min_value=0, max_value=255, value=100, key=f"dg_{i}")
            with c_cols[2]: db = st.number_input("B", min_value=0, max_value=255, value=100, key=f"db_{i}")
            with c_cols[3]: dc = st.number_input("Концентрация", value=5.0, key=f"dc_{i}")
            known_inputs.append([dr, dg, db, dc])
        
    if st.button("➕ ДОБАВИТЬ ТОЧКУ КАЛИБРОВКИ", use_container_width=True):
        st.session_state.extra_rows += 1
        st.rerun()
        
    st.write("---")
    st.markdown("## 🔍 ТЕСТИРУЕМЫЙ ОБРАЗЕЦ")
    
    # Слайдеры для интерактивного подбора цвета цели
    target_r = st.slider("🔴 Красный канал (R)", 0, 255, 120)
    target_g = st.slider("🟢 Зелёный канал (G)", 0, 255, 110)
    target_b = st.slider("🔵 Синий канал (B)", 0, 255, 115)

with col2:
    st.markdown("## 📊 РЕЗУЛЬТАТЫ ЭКСПРЕСС-АНАЛИЗА")
    st.info("ℹ️ Нажмите кнопку ниже, чтобы запустить математические модели ИИ.")
    
    if st.button("🚀 НАЧАТЬ РАСЧЁТ КОНЦЕНТРАЦИИ", type="primary", use_container_width=True):
        target_rgb = [target_r, target_g, target_b]
        euclid, beer, points = calculate_concentration(known_inputs, target_rgb)
        
        st.balloons() # 🎉 Эффект праздничных шаров при успешном расчете!
        
        # Крупные карточки с результатами
        st.metric(
            label="🎯 СПОСОБ 1: МАТРИЦА ЕВКЛИДОВЫХ РАССТОЯНИЙ (RGB)", 
            value=f"{euclid:.2f} ед.",
            delta="Линейный вес"
        )
        st.markdown("> **Как это посчитано:** Модель ищет геометрическое сходство цветового вектора в трёхмерном пространстве RGB относительно опорных калибровочных пробирок.")
        
        st.write("")
        st.metric(
            label="📉 СПОСОБ 2: ЗАКОН БУГЕРА-ЛАМБЕРТА-БЕРА (СПЕКТР)", 
            value=f"{beer:.2f} ед.",
            delta="Оптическая плотность",
            delta_color="inverse"
        )
        st.markdown("> **Как это посчитано:** Модель переводит RGB в физическую величину абсорбции (поглощения света). Это стандарт аналитической химии.")
        
        st.success(f"✅ Анализ завершен успешно! Использовано {points} опорных калибровочных растворов.")
