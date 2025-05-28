import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Seguimiento de Sprint", layout="wide")

st.title("📊 Seguimiento de Sprint - Scrum Master Tool")

# Intenta cargar el CSV o crea un DataFrame vacío
def cargar_datos():
    try:
        return pd.read_csv("sprint_data.csv")
    except FileNotFoundError:
        columnas = ["ID", "Solicitud", "Estado", "Fecha Movimiento", "Sprint", "Persona", "Carryover"]
        return pd.DataFrame(columns=columnas)

# Guardar los datos en CSV
def guardar_datos(df):
    df.to_csv("sprint_data.csv", index=False)

df = cargar_datos()

# Formulario para ingresar datos
with st.form("form_solicitud"):
    st.subheader("➕ Nueva Solicitud")
    solicitud = st.text_input("Nombre o Descripción de la Solicitud")
    estado = st.selectbox("Estado", ["To Do", "In Progress", "Done"])
    fecha_mov = st.date_input("Fecha del Movimiento", value=date.today())
    sprint = st.text_input("Sprint (ej: Sprint 12)")
    persona = st.text_input("Persona Asignada")
    submit = st.form_submit_button("Agregar Solicitud")

    if submit:
        nueva_id = len(df) + 1
        carryover = "Sí" if sprint != f"Sprint {((nueva_id - 1) // 10) + 1}" else "No"  # lógica simple de ejemplo
        nuevo_registro = pd.DataFrame([[nueva_id, solicitud, estado, fecha_mov, sprint, persona, carryover]],
                                      columns=df.columns)
        df = pd.concat([df, nuevo_registro], ignore_index=True)
        guardar_datos(df)
        st.success("✅ Solicitud agregada correctamente.")

# Mostrar datos
st.subheader("📋 Solicitudes Registradas")
st.dataframe(df, use_container_width=True)

# Métricas básicas
st.subheader("📈 Resumen del Sprint")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Solicitudes", len(df))
col2.metric("Completadas (Done)", len(df[df["Estado"] == "Done"]))
col3.metric("Carryovers", len(df[df["Carryover"] == "Sí"]))

# Filtros (opcional)
with st.expander("🔍 Filtros"):
    sprint_filtrado = st.selectbox("Filtrar por Sprint", ["Todos"] + sorted(df["Sprint"].unique()))
    if sprint_filtrado != "Todos":
        st.dataframe(df[df["Sprint"] == sprint_filtrado])
