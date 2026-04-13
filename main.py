import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica
st.set_page_config(page_title="Bayer PDV", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    try:
        # Usamos el secreto que acabas de configurar
        url = st.secrets["URL_SHEET"]
        # El User-Agent ayuda a que Google no bloquee la conexión
        df = pd.read_csv(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        
        # Convertir fecha
        df['Fecha de la visita'] = pd.to_datetime(df['Fecha de la visita'], dayfirst=True)
        
        # Calcular permanencia si las columnas existen
        if 'Primer check-in manual' in df.columns and 'Último check-out manual' in df.columns:
            # Limpieza básica de horas
            df['in'] = pd.to_datetime(df['Fecha de la visita'].dt.date.astype(str) + ' ' + df['Primer check-in manual'].astype(str))
            df['out'] = pd.to_datetime(df['Fecha de la visita'].dt.date.astype(str) + ' ' + df['Último check-out manual'].astype(str))
            df['Permanencia (min)'] = (df['out'] - df['in']).dt.total_seconds() / 60
            df['Permanencia (min)'] = df['Permanencia (min)'].apply(lambda x: x if x > 0 else 0)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

# Ejecución
df = load_data()

if df is not None:
    st.sidebar.title("Filtros Bayer")
    # Selector de fechas
    fechas = st.sidebar.date_input("Rango de fechas", [df['Fecha de la visita'].min(), df['Fecha de la visita'].max()])
    
    if len(fechas) == 2:
        df_filtered = df[(df['Fecha de la visita'].dt.date >= fechas[0]) & (df['Fecha de la visita'].dt.date <= fechas[1])]
    else:
        df_filtered = df

    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Visitas Totales", len(df_filtered))
    c2.metric("Puntos Únicos", df_filtered['Punto de venta'].nunique())
    c3.metric("Promedio Minutos", f"{int(df_filtered['Permanencia (min)'].mean()) if 'Permanencia (min)' in df_filtered.columns else 0}")

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Visitas por Empleado")
        st.bar_chart(df_filtered['Empleado'].value_counts())
    with col2:
        st.subheader("Top 10 Farmacias")
        st.bar_chart(df_filtered['Punto de venta'].value_counts().head(10))

    st.subheader("Detalle Completo")
    st.dataframe(df_filtered)
