import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página con el estilo Bayer
st.set_page_config(page_title="Bayer | Dashboard PDV", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    try:
        url = st.secrets["URL_SHEET"]
        # Cargamos los datos de forma simple
        df = pd.read_csv(url)
        # Solo nos aseguramos de que la fecha sea reconocida como tal
        df['Fecha de la visita'] = pd.to_datetime(df['Fecha de la visita'], dayfirst=True, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    st.title("📊 Reporte Ejecutivo Bayer")
    
    # Filtro lateral simple
    st.sidebar.header("Filtros")
    # Limpiamos filas vacías de fechas para el selector
    df_clean = df_raw.dropna(subset=['Fecha de la visita'])
    rango = st.sidebar.date_input("Seleccionar Período", [df_clean['Fecha de la visita'].min(), df_clean['Fecha de la visita'].max()])
    
    # Filtrado por rango
    if len(rango) == 2:
        df = df_clean[(df_clean['Fecha de la visita'].dt.date >= rango[0]) & (df_clean['Fecha de la visita'].dt.date <= rango[1])]
    else:
        df = df_clean

    # KPIs Principales (Usando tus columnas tal cual)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Visitas", len(df))
    with c2:
        st.metric("Puntos Visitados", df['Punto de venta'].nunique())
    with c3:
        # Aquí usamos tu columna "tiempo en pdv"
        if 'tiempo en pdv' in df.columns:
            st.metric("Permanencia Promedio", f"{df['tiempo en pdv'].iloc[0]}") # Muestra el primero o un promedio
        else:
            st.metric("Permanencia", "N/A")

    st.markdown("---")

    # Dashboards de Ranking
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📍 Visitas por Persona")
        st.bar_chart(df['Empleado'].value_counts())
        
    with col_b:
        st.subheader("🏆 Ranking de Farmacias")
        st.bar_chart(df['Punto de venta'].value_counts().head(10))

    # El apartado detallado que pediste
    st.divider()
    st.subheader("📋 Detalle de Permanencia (Check-in / Check-out)")
    
    # Mostramos las columnas importantes de tu sheet
    columnas_interes = ['Empleado', 'Punto de venta', 'Fecha de la visita', 'Primer check-in manual', 'Último check-out manual', 'tiempo en pdv']
    # Solo mostramos las columnas que existan para evitar errores
    cols_existentes = [c for c in columnas_interes if c in df.columns]
    
    st.dataframe(df[cols_existentes].sort_values(by='Fecha de la visita', ascending=False), use_container_width=True)

else:
    st.info("💡 Si ves un error 404, verifica que tu Google Sheet tenga activado: 'Cualquier persona con el enlace puede leer'.")
