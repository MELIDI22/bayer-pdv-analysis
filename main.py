import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Bayer | Análisis de Visitas", layout="wide")

# Estilo personalizado para mejorar la visual (Sidebar y Botones)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGAR DATOS DESDE LOS SECRETS
@st.cache_data(ttl=600)
def load_data():
    try:
        # Extraemos el link de la "caja fuerte" de Streamlit
        url = st.secrets["URL_SHEET"]
        
        # Leemos el CSV con un User-Agent para evitar el error 404 de Google
        df = pd.read_csv(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        
        # Limpieza de Fechas
        df['Fecha de la visita'] = pd.to_datetime(df['Fecha de la visita'], dayfirst=True)
        
        # Cálculo de permanencia (Check-in vs Check-out)
        # Asumimos que las columnas existen según tu imagen
        if 'Primer check-in manual' in df.columns and 'Último check-out manual' in df.columns:
            fecha_str = df['Fecha de la visita'].dt.strftime('%Y-%m-%d')
            df['in_dt'] = pd.to_datetime(fecha_str + ' ' + df['Primer check-in manual'].astype(str))
            df['out_dt'] = pd.to_datetime(fecha_str + ' ' + df['Último check-out manual'].astype(str))
            df['Permanencia (min)'] = (df['out_dt'] - df['in_dt']).dt.total_seconds() / 60
            # Limpiar valores negativos o erróneos
            df['Permanencia (min)'] = df['Permanencia (min)'].apply(lambda x: x if x > 0 else 0)
            
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # 3. BARRA LATERAL (SIDEBAR) - FILTROS
    st.sidebar.image("https://www.bayer.com/themes/custom/bayer_cpa/logo.svg", width=120)
    st.sidebar.title("Panel de Control")
    
    # Filtro de Rango de Fechas
    min_date = df_raw['Fecha de la visita'].min().date()
    max_date = df_raw['Fecha de la visita'].max().date()
    
    st.sidebar.subheader("📅 Seleccionar Período")
    date_range = st.sidebar.date_input("Rango de fechas", [min_date, max_date])
    
    # Aplicar Filtro
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df_raw[(df_raw['Fecha de la visita'].dt.date >= start_date) & 
                    (df_raw['Fecha de la visita'].dt.date <= end_date)]
    else:
        df = df_raw

    # 4. DASHBOARD PRINCIPAL
    st.title("📊 Análisis Ejecutivo de Visitas PDV")
    
    # KPIs Superiores
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Visitas", len(df))
    with m2:
        st.metric("Puntos Visitados", df['Punto de venta'].nunique())
    with m3:
        promedio = df['Permanencia (min)'].mean() if 'Permanencia (min)' in df.columns else 0
        st.metric("Permanencia Promedio", f"{int(promedio)} min")

    st.markdown("---")

    # 5. GRÁFICOS DE RENDIMIENTO
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📍 Visitas por Empleado")
        emp_counts = df['Empleado'].value_counts().reset_index()
        fig_emp = px.bar(emp_counts, x='count', y='Empleado', orientation='h', 
                         title="Ranking de Personal", color='count', color_continuous_scale='Blues')
        st.plotly_chart(fig_emp, use_container_width=True)

    with col_right:
        st.subheader("🏆 Top Farmacias Visitadas")
        farma_counts = df['Punto de venta'].value_counts().head(10).reset_index()
        fig_farma = px.bar(farma_counts, x='count', y='Punto de venta', orientation='h',
                           title="Ranking de PDV", color_discrete_sequence=['#A5CD39'])
        st.plotly_chart(fig_farma, use_container_width=True)

    # 6. TABLA DETALLADA
    st.markdown("---")
    st.subheader("📋 Detalle de Visitas y Permanencia")
    columnas_ver = ['Empleado', 'Punto de venta', 'Fecha de la visita', 'Primer check-in manual', 'Último check-out manual', 'Permanencia (min)']
    st.dataframe(df[columnas_ver].sort_values(by='Fecha de la visita', ascending=False), use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos. Revisa que el link en 'Secrets' sea el correcto.")
