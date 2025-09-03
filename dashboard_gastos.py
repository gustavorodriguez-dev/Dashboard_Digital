import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# -----------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------
st.set_page_config(
    page_title="Dashboard de Gastos",
    page_icon="💰",
    layout="wide"
)

# -----------------------------
# DISEÑO - TÍTULO
# -----------------------------
st.markdown(
    """
    <div style="background-color:#4CAF50;padding:10px;border-radius:10px">
        <h1 style="color:white;text-align:center;">💰 Dashboard de Gastos Personales</h1>
    </div>
    """, unsafe_allow_html=True
)

# -----------------------------
# SESIÓN PARA GUARDAR DATOS
# -----------------------------
if "gastos" not in st.session_state:
    st.session_state["gastos"] = pd.DataFrame(columns=["Fecha", "Categoría", "Descripción", "Monto"])

# -----------------------------
# FORMULARIO CENTRAL DE CARGA
# -----------------------------
CATEGORIAS = [
    "Comida", 
    "Transporte", 
    "Vivienda", 
    "Ocio", 
    "Salud", 
    "Otros",
    "Agua",
    "Luz",
    "Gas",
    "CISI",
    "Matrícula Profesional",
    "Seguro Auto",
    "Patente Auto",
    "Consultorio"
]

st.markdown("## ➕ Agregar un gasto")
form_col1, form_col2, form_col3 = st.columns([1,2,1])
with form_col2:
    with st.form("form_gasto", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=date.today())
        categoria = st.selectbox("Categoría", CATEGORIAS)
        descripcion = st.text_input("Descripción")
        monto = st.number_input("Monto (Pesos Argentinos)", min_value=0.0, step=100.0)
        submit = st.form_submit_button("Agregar")

if submit:
    nuevo_gasto = pd.DataFrame([[fecha, categoria, descripcion, monto]],
                               columns=["Fecha", "Categoría", "Descripción", "Monto"])
    st.session_state["gastos"] = pd.concat([st.session_state["gastos"], nuevo_gasto], ignore_index=True)
    st.success("✅ Gasto agregado correctamente")

# -----------------------------
# DATOS FILTRADOS Y VISUALIZACIÓN
# -----------------------------
df = st.session_state["gastos"]

if not df.empty:
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)

    # -----------------------------
    # FILTROS
    # -----------------------------
    st.sidebar.header("🔎 Filtrar gastos")
    categorias_filtrar = st.sidebar.multiselect(
        "Categorías a mostrar:",
        options=CATEGORIAS,
        default=CATEGORIAS
    )
    df_filtrado = df[df["Categoría"].isin(categorias_filtrar)]

    # -----------------------------
    # MÉTRICAS DESTACADAS
    # -----------------------------
    st.markdown("### 📊 Resumen General")
    col1, col2, col3 = st.columns(3)
    col1.metric("Gasto Total", f"${df_filtrado['Monto'].sum():,.2f} ARS")
    col2.metric("Gasto Promedio", f"${df_filtrado['Monto'].mean():,.2f} ARS")
    col3.metric("Cantidad de Gastos", len(df_filtrado))

    # -----------------------------
    # GRÁFICOS
    # -----------------------------
    st.markdown("### 📈 Visualización de Gastos")

    graf_col1, graf_col2 = st.columns(2)

    # Gráfico de torta por categoría
    with graf_col1:
        fig_pie = px.pie(
            df_filtrado,
            names="Categoría",
            values="Monto",
            title="Distribución de gastos por categoría",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig_pie.update_traces(textinfo='label+percent', hovertemplate='%{label}: $%{value:,.2f} ARS')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico de barras por mes
    with graf_col2:
        gastos_mes = df_filtrado.groupby("Mes")["Monto"].sum().reset_index()
        fig_bar = px.bar(
            gastos_mes,
            x="Mes",
            y="Monto",
            text_auto=True,
            title="Gastos por mes",
            color="Monto",
            color_continuous_scale="Viridis"
        )
        fig_bar.update_yaxes(title="Pesos Argentinos (ARS)")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Línea de tiempo de gastos
    st.markdown("### 🕒 Evolución diaria de gastos")
    fig_line = px.line(
        df_filtrado,
        x="Fecha",
        y="Monto",
        color="Categoría",
        markers=True,
        title="Gastos diarios por categoría",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_line.update_yaxes(title="Pesos Argentinos (ARS)")
    st.plotly_chart(fig_line, use_container_width=True)

    # -----------------------------
    # TABLA DETALLADA
    # -----------------------------
    st.markdown("### 📋 Detalle de Gastos")
    st.dataframe(df_filtrado.sort_values("Fecha", ascending=False).reset_index(drop=True))
else:
    st.info("👉 Todavía no cargaste ningún gasto. Usá el formulario de arriba.")