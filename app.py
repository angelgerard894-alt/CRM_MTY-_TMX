import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuración inicial ---
st.set_page_config(page_title="CRM Monterrey", layout="wide")

# --- Autenticación con Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import json
credenciales = json.loads(st.secrets["credenciales"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credenciales, scope)
client = gspread.authorize(creds)

# --- Cargar hoja de cálculo ---
sheet = client.open("CRM_CLIENTES_MTY").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# --- Sidebar: Selección de cliente ---
st.sidebar.title("Seleccionar Cliente")
cliente_ids = df["ID"].astype(str).tolist()
selected_id = st.sidebar.selectbox("ID del Cliente", cliente_ids)

cliente = df[df["ID"].astype(str) == selected_id].iloc[0]

# --- Mostrar datos del cliente ---
st.sidebar.markdown("### Datos del Cliente")
st.sidebar.write(f"**Nombre:** {cliente['Nombre']}")
st.sidebar.write(f"**Dirección:** {cliente['Dirección']}")
st.sidebar.write(f"**Estatus actual:** {cliente['Estatus']}")
st.sidebar.write(f"**Comentario actual:** {cliente['Comentario']}")

# --- Edición de campos ---
nuevo_estatus = st.sidebar.selectbox("Actualizar Estatus", ["Pendiente", "Contactado", "Cerrado"])
nuevo_comentario = st.sidebar.text_area("Actualizar Comentario", value=cliente["Comentario"])

# --- Botón para guardar cambios ---
if st.sidebar.button("Guardar Cambios"):
    row_index = df[df["ID"].astype(str) == selected_id].index[0] + 2  # +2 por encabezado y 1-based index
    sheet.update_cell(row_index, df.columns.get_loc("Estatus") + 1, nuevo_estatus)
    sheet.update_cell(row_index, df.columns.get_loc("Comentario") + 1, nuevo_comentario)
    st.sidebar.success("Cambios guardados correctamente.")

# --- Mapa interactivo ---
st.title("📍 Mapa de Clientes - Monterrey")
m = folium.Map(location=[25.6866, -100.3161], zoom_start=11)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df.iterrows():
    folium.Marker(
        location=[row["Latitud"], row["Longitud"]],
        popup=f"""
        <b>{row['Nombre']}</b><br>
        Estatus: {row['Estatus']}<br>
        Comentario: {row['Comentario']}
        """,
        icon=folium.Icon(color="blue" if row["Estatus"] == "Pendiente" else "green")
    ).add_to(marker_cluster)

st_folium(m, width=900, height=600)
