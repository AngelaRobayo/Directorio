import streamlit as st
import pandas as pd
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

# ================================
# Cargar datos
# ================================

solicitudes = cargar_csv("sprint_data.csv", ["ID", "Solicitud", "Estado", "Fecha Movimiento", "Sprint", "Persona", "Carryover"])
sprints = cargar_csv("sprints.csv", ["Sprint", "Fecha Desde", "Fecha Hasta", "Integrantes QA", "Integrantes Dev", "Días Efectivos"])
historial = cargar_csv("historial.csv", ["ID Solicitud", "Fecha", "Campo", "Valor Anterior", "Valor Nuevo"])

# ================================
# Sección: Crear Sprint
# ================================

st.sidebar.header("🛠 Crear Sprint")
with st.sidebar.form("form_sprint"):
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
        st.sidebar.success("✅ Sprint guardado.")

# ================================
# Sección: Agregar/Editar Solicitud
# ================================

st.title("📌 Seguimiento de Solicitudes del Sprint")

with st.form("form_solicitud"):
    st.subheader("➕ Nueva / Actualizar Solicitud")

    id_edit = st.text_input("ID (dejar vacío para nueva)", "")
    solicitud = st.text_input("Descripción de la Solicitud")
    estado = st.selectbox("Estado", ["Por priorizar", "Backlog Desarrollo", "En desarrollo", "Pruebas QA", "Pruebas aceptación"])
    fecha_mov = st.date_input("Fecha del Movimiento", value=date.today())
    sprint = st.selectbox("Asignar a Sprint", options=[""] + list(sprints["Sprint"].unique()))
    persona = st.text_input("Persona Asignada")

    submit = st.form_submit_button("Guardar Solicitud")

    if submit:
        hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if id_edit:
            # Editar
            idx = solicitudes[solicitudes["ID"] == int(id_edit)].index
            if not idx.empty:
                i = idx[0]
                campos = ["Solicitud", "Estado", "Fecha Movimiento", "Sprint", "Persona"]
                valores_nuevos = [solicitud, estado, str(fecha_mov), sprint, persona]
                for campo, nuevo in zip(campos, valores_nuevos):
                    anterior = str(solicitudes.loc[i, campo])
                    if anterior != nuevo:
                        historial = pd.concat([historial, pd.DataFrame([[id_edit, hoy, campo, anterior, nuevo]], columns=historial.columns)], ignore_index=True)
                        solicitudes.loc[i, campo] = nuevo
                guardar_csv(solicitudes, "sprint_data.csv")
                guardar_csv(historial, "historial.csv")
                st.success("📝 Solicitud actualizada.")
            else:
                st.warning("⚠️ ID no encontrado.")
        else:
            nuevo_id = 1 if solicitudes.empty else int(solicitudes["ID"].max()) + 1
            carryover = "No"  # inicial
            nueva = pd.DataFrame([[nuevo_id, solicitud, estado, fecha_mov, sprint, persona, carryover]], columns=solicitudes.columns)
            solicitudes = pd.concat([solicitudes, nueva], ignore_index=True)
            guardar_csv(solicitudes, "sprint_data.csv")
            st.success("✅ Solicitud agregada.")

# ================================
# Mostrar Solicitudes
# ================================

st.subheader("📋 Solicitudes Registradas")
st.dataframe(solicitudes, use_container_width=True)

# ================================
# Mostrar Historial de Cambios
# ================================

st.subheader("🕒 Historial de Actualizaciones")
st.dataframe(historial.sort_values(by="Fecha", ascending=False), use_container_width=True)

# ================================
# Métricas
# ================================

st.subheader("📊 Resumen General")
col1, col2, col3 = st.columns(3)
col1.metric("Solicitudes Totales", len(solicitudes))
col2.metric("Estados únicos", len(solicitudes["Estado"].unique()))
col3.metric("Total de actualizaciones", len(historial))
