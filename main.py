import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO "FRUTIKA/BAYER"
st.set_page_config(page_title="Bayer – Dashboard Farmacias", layout="wide")

# Inyectamos el CSS que me pasaste para que se vea igual
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;800&family=Barlow:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Barlow', sans-serif;
        background-color: #F4F8FC;
    }}
    
    .stMetric {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #00BCDD;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    h1, h2, h3 {{
        font-family: 'Barlow Condensed', sans-serif;
        color: #003865;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .bayer-header {{
        background-color: #001E3C;
        padding: 1.5rem;
        border-radius: 0 0 15px 15px;
        margin-bottom: 2rem;
        border-left: 8px solid #A5CD39;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def load_data():
    try:
        url = st.secrets["URL_SHEET"]
        df = pd.read_csv(url, storage_options={'User-Agent': 'Mozilla/5.0'})
        df['Fecha de la visita'] = pd.to_datetime(df['Fecha de la visita'], dayfirst=True, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

df_raw = load_data()

if df_raw is not None:
    # HEADER ESTILO PRO
    st.markdown("""
        <div class="bayer-header">
            <h1 style='color: white; margin:0;'>BAYER | DASHBOARD v4.1</h1>
            <p style='color: #00BCDD; font-weight:600; margin:0;'>PDV SUMMARY + INFORME EJECUTIVO</p>
        </div>
    """, unsafe_allow_html=True)

    # FILTROS LATERALES
    st.sidebar.header("CONFIGURACIÓN")
    df_clean = df_raw.dropna(subset=['Fecha de la visita'])
    
    if not df_clean.empty:
        rango = st.sidebar.date_input("Periodo de Análisis", 
                                     [df_clean['Fecha de la visita'].min(), 
                                      df_clean['Fecha de la visita'].max()])
        
        if len(rango) == 2:
            df = df_clean[(df_clean['Fecha de la visita'].dt.date >= rango[0]) & 
                          (df_clean['Fecha de la visita'].dt.date <= rango[1])]
        else:
            df = df_clean
    else:
        df = df_raw

    # 3. KPI CARDS (Réplica del diseño HTML)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("TOTAL VISITAS", len(df))
    with k2:
        st.metric("PDVs ACTIVOS", df['Punto de venta'].nunique())
    with k3:
        # Usamos tu columna calculada
        val_tiempo = df['tiempo en pdv'].iloc[0] if 'tiempo en pdv' in df.columns and not df.empty else "0 min"
        st.metric("PERMANENCIA", str(val_tiempo))
    with k4:
        st.metric("EQUIPO", df['Empleado'].nunique() if 'Empleado' in df.columns else 0)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. GRÁFICOS CON COLORES BAYER
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📍 COBERTURA POR EMPLEADO")
        fig_emp = px.bar(df['Empleado'].value_counts().reset_index(), 
                         x='count', y='Empleado', orientation='h',
                         color_discrete_sequence=['#00BCDD']) # Teal Bayer
        fig_emp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_emp, use_container_width=True)

    with col_right:
        st.subheader("🏆 TOP FARMACIAS")
        fig_pdv = px.pie(df['Punto de venta'].value_counts().head(5).reset_index(), 
                         values='count', names='Punto de venta',
                         color_discrete_sequence=['#003865', '#00BCDD', '#A5CD39', '#001E3C', '#E8F4FB'])
        st.plotly_chart(fig_pdv, use_container_width=True)

    # 5. TABLA DE DATOS ESTILO INFORME
    st.subheader("📋 DETALLE DE GESTIÓN EN CAMPO")
    cols_interes = ['Empleado', 'Punto de venta', 'Fecha de la visita', 'tiempo en pdv']
    existentes = [c for c in cols_interes if c in df.columns]
    
    st.dataframe(df[existentes].style.set_properties(**{
        'background-color': 'white',
        'color': '#003865',
        'border-color': '#E8F4FB'
    }), use_container_width=True)

else:
    st.warning("Cargando base de datos...")
