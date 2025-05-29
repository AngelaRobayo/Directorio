import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

st.set_page_config(page_title="Seguimiento de Sprint", layout="wide")

# Columnas base actualizadas
columnas_solicitudes = [
    "ID", "Solicitud", "Tipo Solicitud", "Estado", "Fecha Movimiento",
    "Sprint", "Carryover", "Puntos QA", "Puntos Dev", "Puntos Finales",  # Añadir Puntos Finales
    "Compromiso", "HU Relacionada", "Tiempo Resolución (h)"
]

columnas_historial = columnas_solicitudes + ["Fecha Cambio", "Cambio"]

fibonacci_options = ["No aplica", 1, 2, 3, 5, 8, 13, 21]

def asegurar_columnas(df, columnas):
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    return df[columnas]

def cargar_csv(nombre, columnas):
    if not os.path.exists(nombre):
        return pd.DataFrame(columns=columnas)
    df = pd.read_csv(nombre)
    return asegurar_columnas(df, columnas)

def guardar_csv(df, nombre):
    df.to_csv(nombre, index=False)

# Cargar datos
solicitudes = cargar_csv("sprint_data.csv", columnas_solicitudes)
sprints = cargar_csv("sprints.csv", ["Sprint", "Fecha Desde", "Fecha Hasta", "Integrantes QA", "Integrantes Dev", "Días Efectivos"])
historial = cargar_csv("historial.csv", columnas_historial)

# Crear Sprint
with st.expander("🛠 Crear Sprint"):
    with st.form("form_sprint"):
        sprint_name = st.text_input("Nombre del Sprint")
        fecha_desde = st.date_input("Fecha desde")
        fecha_hasta = st.date_input("Fecha hasta")
        qa = st.number_input("Integrantes QA", min_value=0)
        dev = st.number_input("Integrantes Desarrollo", min_value=0)
        dias_efectivos = st.number_input("Días efectivos del sprint", min_value=1)
        submit_sprint = st.form_submit_button("Guardar Sprint")
        if submit_sprint:
            sprints = pd.concat([sprints, pd.DataFrame([[sprint_name, fecha_desde, fecha_hasta, qa, dev, dias_efectivos]], columns=sprints.columns)], ignore_index=True)
            guardar_csv(sprints, "sprints.csv")
            st.success("Sprint guardado.")

# Solicitudes
st.title("📌 Seguimiento de Solicitudes")


with st.expander("✏️ Modificar Solicitud Existente"):
    with st.form("form_modificar_solicitud"):
        id_edit = st.text_input("ID de Solicitud existente a modificar")
        
        if id_edit and id_edit.isdigit() and int(id_edit) in solicitudes["ID"].values:
            solicitud_data = solicitudes[solicitudes["ID"] == int(id_edit)].iloc[0]
            st.write("**Descripción:**", solicitud_data["Solicitud"])
            st.write("**Tipo de Solicitud:**", solicitud_data["Tipo Solicitud"])

            estado = st.selectbox("Estado", ["Por priorizar", "Backlog Desarrollo", "En desarrollo", "Pruebas QA", "Pruebas aceptación"], index=["Por priorizar", "Backlog Desarrollo", "En desarrollo", "Pruebas QA", "Pruebas aceptación"].index(solicitud_data["Estado"]))
            fecha_mov = st.date_input("Fecha de Movimiento", value=pd.to_datetime(solicitud_data["Fecha Movimiento"]))
            sprint = st.selectbox("Sprint", [""] + list(sprints["Sprint"].unique()), index=0 if solicitud_data["Sprint"] == "" else list(sprints["Sprint"].unique()).index(solicitud_data["Sprint"]))
            carryover = st.checkbox("¿Es Carryover?", value=(solicitud_data["Carryover"] == "Sí"))
            puntos_qa = st.selectbox("Puntos QA", fibonacci_options, index=fibonacci_options.index(solicitud_data["Puntos QA"]) if solicitud_data["Puntos QA"] in fibonacci_options else 0)
            puntos_dev = st.selectbox("Puntos Dev", fibonacci_options, index=fibonacci_options.index(solicitud_data["Puntos Dev"]) if solicitud_data["Puntos Dev"] in fibonacci_options else 0)
            compromiso = st.selectbox("Compromiso del equipo", ["Desarrollo", "QA", "Ambos"], index=["Desarrollo", "QA", "Ambos"].index(solicitud_data["Compromiso"]))

            id_hu = st.text_input("ID HU Relacionada (opcional)", value=solicitud_data["HU Relacionada"])
            tiempo_res = st.number_input("Tiempo de Resolución (h)", min_value=0.0, step=0.5, value=float(solicitud_data["Tiempo Resolución (h)"]) if pd.notna(solicitud_data["Tiempo Resolución (h)"]) and solicitud_data["Tiempo Resolución (h)"] != "" else 0.0)

            # Botón de submit dentro del formulario
            if st.form_submit_button("Guardar Cambios"):
                hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                idx = solicitudes[solicitudes["ID"] == int(id_edit)].index[0]
                solicitudes.loc[idx, ["Estado", "Fecha Movimiento", "Sprint", "Carryover", "Puntos QA", "Puntos Dev", "Compromiso", "HU Relacionada", "Tiempo Resolución (h)"]] = [
                    estado, fecha_mov, sprint, "Sí" if carryover else "No",
                    str(puntos_qa), str(puntos_dev), compromiso, id_hu, tiempo_res
                ]

                # Registrar el cambio en el historial
                historial_reg = solicitudes.loc[[idx]].copy()
                historial_reg["Fecha Cambio"] = hoy
                historial_reg["Cambio"] = "Actualización"
                historial = pd.concat([historial, historial_reg], ignore_index=True)

                # Guardar los datos en los CSVs
                guardar_csv(solicitudes, "sprint_data.csv")
                guardar_csv(historial, "historial.csv")

                st.success("✅ Solicitud modificada exitosamente.")
        elif id_edit:
            st.warning("⚠️ El ID no existe o no es válido.")

with st.expander("🆕 Crear Nueva Solicitud"):
    with st.form("form_crear_solicitud"):
        id_nuevo = st.text_input("ID (único)")
        solicitud = st.text_input("Descripción")
        tipo = st.selectbox("Tipo de Solicitud", ["Historia de usuario", "Deuda Técnica", "Defecto"])
        estado = st.selectbox("Estado", ["Por priorizar", "Backlog Desarrollo", "En desarrollo", "Pruebas QA", "Pruebas aceptación"])
        fecha_mov = st.date_input("Fecha de Movimiento", value=date.today())
        sprint = st.selectbox("Sprint", [""] + list(sprints["Sprint"].unique()))
        carryover = st.checkbox("¿Es Carryover?")
        puntos_qa = st.selectbox("Puntos QA", fibonacci_options)
        puntos_dev = st.selectbox("Puntos Dev", fibonacci_options)
        puntos_finales = st.selectbox("Puntos Finales", fibonacci_options)
        compromiso = st.selectbox("Compromiso del equipo", ["Desarrollo", "QA", "Ambos"])

        id_hu = ""
        tiempo_res = ""
        if tipo == "Defecto":
            id_hu = st.text_input("ID HU Relacionada (opcional)")
            tiempo_res = st.number_input("Tiempo de Resolución (h)", min_value=0.0, step=0.5)

        submit_crear_solicitud = st.form_submit_button("Guardar Nueva Solicitud")
        if submit_crear_solicitud:
            hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not id_nuevo.isdigit():
                st.error("ID debe ser un número entero válido.")
            elif int(id_nuevo) in solicitudes["ID"].values:
                st.error("Este ID ya existe. Usa el formulario de modificación.")
            else:
                fila = [
                    int(id_nuevo), solicitud, tipo, estado, fecha_mov, sprint,
                    "Sí" if carryover else "No", str(puntos_qa), str(puntos_dev),
                    str(puntos_finales), compromiso, id_hu, tiempo_res
                ]
                nueva_df = pd.DataFrame([fila], columns=columnas_solicitudes)
                solicitudes = pd.concat([solicitudes, nueva_df], ignore_index=True)
                nueva_df["Fecha Cambio"] = hoy
                nueva_df["Cambio"] = "Nuevo"
                historial = pd.concat([historial, nueva_df], ignore_index=True)
                guardar_csv(solicitudes, "sprint_data.csv")
                guardar_csv(historial, "historial.csv")
                st.success("✅ Solicitud creada.")



# Mostrar solicitudes
st.subheader("📋 Solicitudes Registradas")

filtro_sprint = st.selectbox("🔎 Filtrar por Sprint", ["Todos"] + list(sprints["Sprint"].unique()))
filtro_estado = st.selectbox("🔎 Filtrar por Estado", ["Todos"] + sorted(solicitudes["Estado"].unique()))
filtro_id = st.text_input("🔍 Buscar por ID")

df_filtrado = solicitudes.copy()
if filtro_sprint != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Sprint"] == filtro_sprint]
if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]
if filtro_id:
    df_filtrado = df_filtrado[df_filtrado["ID"].astype(str).str.contains(filtro_id.strip())]

st.dataframe(df_filtrado, use_container_width=True)

# Historial
st.subheader("🕒 Historial de Cambios")

historial["Fecha Cambio"] = pd.to_datetime(historial["Fecha Cambio"], errors='coerce')
historial["Fecha Movimiento"] = pd.to_datetime(historial["Fecha Movimiento"], errors='coerce')

col1, col2, col3 = st.columns(3)
with col1:
    filtro_hist_sprint = st.selectbox("📌 Sprint (Historial)", ["Todos"] + list(sprints["Sprint"].unique()))
with col2:
    aplicar_fechas = st.checkbox("📅 Filtrar por fechas (Historial)")
with col3:
    filtro_hist_id = st.text_input("🔍 Buscar por ID (Historial)")

hist_filtrado = historial.copy()
if filtro_hist_sprint != "Todos":
    hist_filtrado = hist_filtrado[hist_filtrado["Sprint"] == filtro_hist_sprint]
if aplicar_fechas:
    fecha_ini = st.date_input("Desde (Historial)", date.today().replace(month=1, day=1))
    fecha_fin = st.date_input("Hasta (Historial)", date.today())
    hist_filtrado = hist_filtrado[
        (hist_filtrado["Fecha Cambio"] >= pd.to_datetime(fecha_ini)) &
        (hist_filtrado["Fecha Cambio"] <= pd.to_datetime(fecha_fin))
    ]
if filtro_hist_id:
    hist_filtrado = hist_filtrado[hist_filtrado["ID"].astype(str).str.contains(filtro_hist_id.strip())]

st.dataframe(hist_filtrado[columnas_historial], use_container_width=True)

# Resumen
st.subheader("📊 Resumen General por Sprint")

resumen = hist_filtrado.copy()
resumen["Puntos QA"] = pd.to_numeric(resumen["Puntos QA"].replace("No aplica", 0), errors="coerce").fillna(0)
resumen["Puntos Dev"] = pd.to_numeric(resumen["Puntos Dev"].replace("No aplica", 0), errors="coerce").fillna(0)
resumen["Puntos Finales"] = pd.to_numeric(resumen["Puntos Finales"].replace("No aplica", 0), errors="coerce").fillna(0)
resumen["Tiempo Resolución (h)"] = pd.to_numeric(resumen["Tiempo Resolución (h)"], errors="coerce").fillna(0)

if not resumen.empty:
    resumen_agg = resumen.groupby("Sprint").agg(
        Total_Solicitudes=("ID", "nunique"),
        Total_Carryover=("Carryover", lambda x: (x == "Sí").sum()),
        Puntos_QA=("Puntos QA", "sum"),
        Puntos_Dev=("Puntos Dev", "sum"),
        Puntos_Finales=("Puntos Finales", "sum"),
        QA_only=("Compromiso", lambda x: (x == "QA").sum()),
        Dev_only=("Compromiso", lambda x: (x == "Desarrollo").sum()),
        Ambos=("Compromiso", lambda x: (x == "Ambos").sum()),
        Tiempo_Resolucion_Prom=("Tiempo Resolución (h)", "mean")
    ).reset_index()

    resumen_completo = pd.merge(resumen_agg, sprints, how="left", on="Sprint")
    resumen_completo = resumen_completo[[
        "Sprint", "Total_Solicitudes", "Total_Carryover",
        "Integrantes QA", "Integrantes Dev", "QA_only", "Dev_only", "Ambos",
        "Tiempo_Resolucion_Prom", "Fecha Desde", "Fecha Hasta"
    ]]

    st.dataframe(resumen_completo, use_container_width=True)
else:
    st.info("⚠️ No hay datos para mostrar.")
