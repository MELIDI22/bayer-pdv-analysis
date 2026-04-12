import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Di | Bayer PDV Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. CARGAR EL DISEÑO VISUAL (CSS)
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

# 3. CONEXIÓN A DATOS (GOOGLE SHEETS)
@st.cache_data(ttl=600)
def load_data():
    try:
        # Intenta leer el link secreto que configuraremos en Streamlit
        sheet_url = st.secrets["URL_SHEET"]
        df = pd.read_csv(sheet_url)
        return df
    except:
        # Si aún no hay link, muestra datos de ejemplo para que veas el diseño
        return pd.DataFrame({
            'Producto': ['Aspirina', 'Redoxon', 'Alka-Seltzer', 'Bepanthen'],
            'Ventas': [15000, 12000, 8000, 5000],
            'Meta': [20000, 10000, 10000, 4000]
        })

df = load_data()

# 4. ENCABEZADO PERSONALIZADO (HTML)
st.markdown("""
    <div class="custom-header">
        <div>
            <h1>Dashboard de Análisis de Visitas</h1>
            <p>Panel Ejecutivo de Gestión PDV | Bayer</p>
        </div>
        <div style="margin-left: auto; color: white; font-weight: bold; font-size: 1.2rem;">
            By Di
        </div>
    </div>
""", unsafe_allow_html=True)

# 5. INDICADORES CLAVE (KPIs)
col1, col2, col3 = st.columns(3)

# Cálculos simples
v_total = df.iloc[:, 1].sum() if len(df.columns) > 1 else 0 # Suma de la segunda columna
meta_total = df.iloc[:, 2].sum() if len(df.columns) > 2 else 1
cumplimiento = (v_total / meta_total) * 100

with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Ventas Totales</div><div class="kpi-value">${v_total:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Cumplimiento</div><div class="kpi-value">{cumplimiento:.1f}%</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Productos</div><div class="kpi-value">{len(df)}</div></div>', unsafe_allow_html=True)

# 6. GRÁFICOS INTERACTIVOS
st.markdown("### Rendimiento por Categoría")
fig = px.bar(df, x=df.columns[0], y=df.columns[1], 
             color_discrete_sequence=['#00BCDD'], # Color Teal Bayer
             template="plotly_white")

fig.update_layout(font_family="Barlow", plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# 7. BOTÓN PARA DESCARGAR PDF
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(40, 10, "Informe Ejecutivo de Visitas - Bayer")
    pdf.ln(20)
    pdf.set_font("Arial", '', 12)
    pdf.cell(40, 10, f"Resumen generado por Di")
    return pdf.output(dest='S').encode('latin-1')

st.download_button(
    label="Descargar Reporte en PDF",
    data=create_pdf(df),
    file_name="reporte_bayer.pdf",
    mime="application/pdf"
)
