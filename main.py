import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. CONFIGURACIÓN Y MODO OSCURO (SIMULADO PARA MÁXIMA COMPATIBILIDAD)
st.set_page_config(page_title="Bayer | PDV Analysis", layout="wide")

# Sidebar para Filtros
st.sidebar.image("https://www.bayer.com/themes/custom/bayer_cpa/logo.svg", width=100)
st.sidebar.title("Filtros de Control")

# 2. CARGAR DATOS
@st.cache_data
def load_data():
    url = st.secrets["URL_SHEET"]
    df = pd.read_csv(url)
    # Limpieza de fechas y horas
    df['Fecha de la visita'] = pd.to_datetime(df['Fecha de la visita'], dayfirst=True)
    # Combinar fecha con hora para calcular permanencia
    df['Check-in'] = pd.to_datetime(df['Fecha de la visita'].dt.strftime('%Y-%m-%d') + ' ' + df['Primer check-in manual'])
    df['Check-out'] = pd.to_datetime(df['Fecha de la visita'].dt.strftime('%Y-%m-%d') + ' ' + df['Último check-out manual'])
    df['Permanencia'] = (df['Check-out'] - df['Check-in']).dt.total_seconds() / 60
    return df

try:
    df_raw = load_data()

    # 3. FILTRO DE FECHAS
    col_f1, col_f2 = st.sidebar.columns(2)
    with col_f1:
        start_date = st.date_input("Desde", df_raw['Fecha de la visita'].min())
    with col_f2:
        end_date = st.date_input("Hasta", df_raw['Fecha de la visita'].max())

    # Filtrar DataFrame
    mask = (df_raw['Fecha de la visita'].dt.date >= start_date) & (df_raw['Fecha de la visita'].dt.date <= end_date)
    df = df_raw.loc[mask]

    # 4. HEADER MÉTRICAS (Directorio)
    st.markdown(f"## 📊 Reporte Ejecutivo: {start_date} al {end_date}")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Total Visitas en Rango", len(df))
    with kpi2:
        st.metric("PDV Únicos Visitados", df['Punto de venta'].nunique())
    with kpi3:
        # Promedio de permanencia
        avg_time = df['Permanencia'].mean()
        st.metric("Promedio Permanencia", f"{avg_time:.1f} min")

    st.divider()

    # 5. DASHBOARDS ACTUALIZABLES
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📍 Visitas por Persona")
        ranking_persona = df['Empleado'].value_counts().reset_index()
        fig_pers = px.bar(ranking_persona, x='count', y='Empleado', orientation='h', 
                          color='count', color_continuous_scale='Blues', template="simple_white")
        st.plotly_chart(fig_pers, use_container_width=True)

    with col_right:
        st.subheader("🏆 Ranking Farmacias")
        ranking_farma = df['Punto de venta'].value_counts().reset_index().head(10)
        fig_farma = px.bar(ranking_farma, x='count', y='Punto de venta', orientation='h',
                           color_discrete_sequence=['#A5CD39'], template="simple_white")
        st.plotly_chart(fig_farma, use_container_width=True)

    # 6. APARTADO DETALLADO (Check-in/Out)
    st.divider()
    st.subheader("📋 Detalle de Permanencia por Punto de Venta")
    
    # Seleccionar solo columnas necesarias para el directorio
    df_detalle = df[['Empleado', 'Punto de venta', 'Fecha de la visita', 'Primer check-in manual', 'Último check-out manual', 'Permanencia']].copy()
    df_detalle['Permanencia'] = df_detalle['Permanencia'].apply(lambda x: f"{int(x)} min" if x > 0 else "N/A")
    
    st.dataframe(df_detalle.sort_values(by='Fecha de la visita', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Esperando conexión con Google Sheets... {e}")
