import streamlit as st
import pandas as pd
import os
from datetime import date, datetime



st.set_page_config(page_title="Seguimiento de Sprint", layout="wide")

# ================================
# Funciones auxiliares
# ================================

def cargar_csv(nombre_archivo, columnas):
    try:
        return pd.read_csv(nombre_archivo)
    except FileNotFoundError:
        return pd.DataFrame(columns=columnas)

def guardar_csv(df, nombre_archivo):
    df.to_csv(nombre_archivo, index=False)

fibonacci_options = ["No aplica", 1, 2, 3, 5, 8, 13, 21]

# ================================
# Cargar datos
# ================================

columnas_base = ["ID", "Solicitud", "Estado", "Fecha Movimiento", "Sprint", "Persona", "Carryover", "Puntos QA", "Puntos Dev"]
solicitudes = cargar_csv("sprint_data.csv", columnas_base)
sprints = cargar_csv("sprints.csv", ["Sprint", "Fecha Desde", "Fecha Hasta", "Integrantes QA", "Integrantes Dev", "Días Efectivos"])
historial = cargar_csv("historial.csv", columnas_base + ["Fecha Cambio", "Cambio"])

# ================================
# Crear Sprint (expander)
# ================================

with st.expander("🛠 Crear Sprint"):
    with st.form("form_sprint"):
        sprint_name = st.text_input("Nombre del Sprint (ej: Sprint 10)")
        fecha_desde = st.date_input("Fecha desde")
        fecha_hasta = st.date_input("Fecha hasta")
        qa = st.number_input("Integrantes QA", min_value=0, step=1)
        dev = st.number_input("Integrantes Desarrollo", min_value=0, step=1)
        dias_efectivos = st.number_input("Días efectivos del sprint", min_value=1, step=1)
        submit_sprint = st.form_submit_button("Guardar Sprint")

        if submit_sprint:
            nuevo_sprint = pd.DataFrame([[sprint_name, fecha_desde, fecha_hasta, qa, dev, dias_efectivos]], columns=sprints.columns)
            sprints = pd.concat([sprints, nuevo_sprint], ignore_index=True)
            guardar_csv(sprints, "sprints.csv")
            st.success("✅ Sprint guardado.")

# ================================
# Nueva o Actualizar Solicitud
# ================================

st.title("📌 Seguimiento de Solicitudes")

with st.expander("➕ Nueva / Actualizar Solicitud"):
    with st.form("form_solicitud"):
        id_edit = st.text_input("ID (dejar vacío para nueva)", "")
        solicitud = st.text_input("Descripción de la Solicitud")
        estado = st.selectbox("Estado", ["Por priorizar", "Backlog Desarrollo", "En desarrollo", "Pruebas QA", "Pruebas aceptación"])
        fecha_mov = st.date_input("Fecha del Movimiento", value=date.today())
        sprint = st.selectbox("Asignar a Sprint", options=[""] + list(sprints["Sprint"].unique()))
        persona = st.text_input("Persona Asignada")
        carryover = st.checkbox("¿Es Carryover?")
        puntos_qa = st.selectbox("Puntos QA", fibonacci_options)
        puntos_dev = st.selectbox("Puntos Desarrollo", fibonacci_options)

        submit = st.form_submit_button("Guardar Solicitud")

        if submit:
            hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            puntos_qa_str = str(puntos_qa)
            puntos_dev_str = str(puntos_dev)

            if id_edit:
                idx = solicitudes[solicitudes["ID"] == int(id_edit)].index
                if not idx.empty:
                    i = idx[0]
                    old_row = solicitudes.loc[i].copy()
                    solicitudes.loc[i] = [int(id_edit), solicitud, estado, fecha_mov, sprint, persona,
                                          "Sí" if carryover else "No", puntos_qa_str, puntos_dev_str]

                    cambio = pd.Series(solicitudes.loc[i])
                    cambio["Fecha Cambio"] = hoy
                    cambio["Cambio"] = "Actualización"
                    historial = pd.concat([historial, pd.DataFrame([cambio])], ignore_index=True)

                    guardar_csv(solicitudes, "sprint_data.csv")
                    guardar_csv(historial, "historial.csv")
                    st.success("📝 Solicitud actualizada.")
                else:
                    st.warning("⚠️ ID no encontrado.")
            else:
                nuevo_id = 1 if solicitudes.empty else int(solicitudes["ID"].max()) + 1
                nueva = pd.DataFrame([[nuevo_id, solicitud, estado, fecha_mov, sprint, persona,
                                       "Sí" if carryover else "No", puntos_qa_str, puntos_dev_str]],
                                     columns=solicitudes.columns)
                solicitudes = pd.concat([solicitudes, nueva], ignore_index=True)

                cambio = nueva.copy()
                cambio["Fecha Cambio"] = hoy
                cambio["Cambio"] = "Nuevo"
                historial = pd.concat([historial, cambio], ignore_index=True)

                guardar_csv(solicitudes, "sprint_data.csv")
                guardar_csv(historial, "historial.csv")
                st.success("✅ Solicitud agregada.")

# ================================
# Solicitudes Registradas
# ================================

st.subheader("📋 Solicitudes Registradas")

filtro_sprint = st.selectbox("🔍 Filtrar por Sprint", ["Todos"] + list(sprints["Sprint"].unique()))
filtro_estado = st.selectbox("🔍 Filtrar por Estado", ["Todos"] + sorted(solicitudes["Estado"].unique()))

df_filtrado = solicitudes.copy()
if filtro_sprint != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Sprint"] == filtro_sprint]
if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]

st.dataframe(df_filtrado, use_container_width=True)

# ================================
# Historial de Actualizaciones
# ================================

st.subheader("🕒 Historial de Cambios")
filtro_hist_sprint = st.selectbox("🔍 Filtrar historial por Sprint", ["Todos"] + list(sprints["Sprint"].unique()), key="hist")

hist_filtrado = historial.copy()
if filtro_hist_sprint != "Todos":
    hist_filtrado = hist_filtrado[hist_filtrado["Sprint"] == filtro_hist_sprint]

st.dataframe(hist_filtrado[columnas_base + ["Fecha Cambio", "Cambio"]], use_container_width=True)

# ================================
# Resumen por Sprint
# ================================

st.subheader("📊 Resumen por Sprint")

for sprint_nombre in sprints["Sprint"].unique():
    df_sprint = solicitudes[solicitudes["Sprint"] == sprint_nombre]
    total = len(df_sprint)
    carryover_count = (df_sprint["Carryover"] == "Sí").sum()
    puntos_qa = pd.to_numeric(df_sprint["Puntos QA"].replace("No aplica", 0)).sum()
    puntos_dev = pd.to_numeric(df_sprint["Puntos Dev"].replace("No aplica", 0)).sum()

    st.markdown(f"### Sprint: {sprint_nombre}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Solicitudes", total)
    col2.metric("Carryover", carryover_count)
    col3.metric("Puntos QA", puntos_qa)
    col4.metric("Puntos Dev", puntos_dev)
