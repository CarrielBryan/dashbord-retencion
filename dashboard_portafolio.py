import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import os
from PIL import Image

# Configuración visual
st.set_page_config(page_title="Dashboard de Retención", layout="wide")

# Estilo CSS personalizado
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        .stDownloadButton button {
            background-color: #2E86C1;
            color: white;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: #154360;
        }
    </style>
""", unsafe_allow_html=True)

# Encabezado con introducción
st.title("Dashboard de Análisis de Retención de Clientes")
# logo = Image.open("logo.png")
# st.image(logo, width=120)

st.write("""
### Proyecto de Retención de Clientes
Este dashboard analiza el comportamiento de cancelaciones, retención y resultados de llamadas a clientes.

A través de visualizaciones claras, puedes explorar patrones de cancelación por región, tipo de plan y motivo.
""")
st.markdown("---")

# Cargar base de datos
if not os.path.exists("retencion.db"):
    st.error("La base de datos 'retencion.db' no fue encontrada. Ejecuta primero 'ret_bd.py'.")
    st.stop()

conn = sqlite3.connect("retencion.db")

try:
    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    contratos = pd.read_sql_query("SELECT * FROM contratos", conn)
    cancelaciones = pd.read_sql_query("SELECT * FROM cancelaciones", conn)
    llamadas = pd.read_sql_query("SELECT * FROM llamadas_retencion", conn)
except Exception as e:
    st.error(f"Error al cargar tablas: {e}")
    conn.close()
    st.stop()

conn.close()

sns.set_theme(style="whitegrid", palette="pastel")

df = clientes.copy()
df = df.merge(contratos, left_on='id', right_on='cliente_id', how='left')
if 'id_x' in df.columns:
    df.rename(columns={'id_x': 'id'}, inplace=True)
df = df.merge(cancelaciones, left_on='id', right_on='cliente_id', how='left', suffixes=('', '_cancel'))
df = df.merge(llamadas, left_on='id', right_on='cliente_id', how='left', suffixes=('', '_llamada'))

if 'fecha_cancelacion_cancel' in df.columns:
    df['cancelado'] = df['fecha_cancelacion_cancel'].notnull()
elif 'fecha_cancelacion' in df.columns:
    df['cancelado'] = df['fecha_cancelacion'].notnull()
else:
    st.error("No se encontró la columna 'fecha_cancelacion'.")
    st.stop()

# Filtros
st.sidebar.header("Filtros")
region_sel = st.sidebar.multiselect("Región", df['region'].dropna().unique(), default=df['region'].dropna().unique())
plan_sel = st.sidebar.multiselect("Tipo de Plan", df['tipo_plan'].dropna().unique(), default=df['tipo_plan'].dropna().unique())

df_filtrado = df[(df['region'].isin(region_sel)) & (df['tipo_plan'].isin(plan_sel))]

# KPIs
st.markdown("### Indicadores Clave")
col1, col2, col3 = st.columns(3)
col1.metric("Clientes Totales", df_filtrado['id'].nunique())
col2.metric("Cancelaciones", df_filtrado['cancelado'].sum())
cancel_rate = df_filtrado['cancelado'].mean() * 100
col3.metric("Tasa de Cancelación", f"{cancel_rate:.2f}%")
st.markdown("---")

# Gráficos
st.subheader("Tasa de Cancelación por Región")
cancel_region = df_filtrado.groupby('region')['cancelado'].mean() * 100
fig1, ax1 = plt.subplots()
sns.barplot(x=cancel_region.index, y=cancel_region.values, ax=ax1)
ax1.set_ylabel("Tasa de Cancelación (%)")
st.pyplot(fig1)
st.markdown("---")

st.subheader("Tasa de Cancelación por Tipo de Plan")
cancel_plan = df_filtrado.groupby('tipo_plan')['cancelado'].mean() * 100
fig2, ax2 = plt.subplots()
sns.barplot(x=cancel_plan.index, y=cancel_plan.values, ax=ax2)
ax2.set_ylabel("Tasa de Cancelación (%)")
st.pyplot(fig2)
st.markdown("---")

st.subheader("Motivos de Cancelación")
motivos = df_filtrado[df_filtrado['cancelado']]['motivo'].value_counts()
fig3, ax3 = plt.subplots()
sns.barplot(x=motivos.index, y=motivos.values, ax=ax3)
ax3.set_ylabel("Cantidad")
ax3.set_xticklabels(motivos.index, rotation=45)
st.pyplot(fig3)
st.markdown("---")

st.subheader("Efectividad de Llamadas de Retención")
llamadas_filtradas = df_filtrado[df_filtrado['resultado'].notnull()]
efectividad = llamadas_filtradas['resultado'].value_counts(normalize=True) * 100
fig4, ax4 = plt.subplots()
sns.barplot(x=efectividad.index, y=efectividad.values, ax=ax4)
ax4.set_ylabel("Porcentaje")
st.pyplot(fig4)
st.markdown("---")
