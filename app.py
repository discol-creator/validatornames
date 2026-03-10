import streamlit as st
import pandas as pd
import unicodedata

# Configuración de la página
st.set_page_config(page_title="Comparador de Encuestas", layout="wide")

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    # Elimina tildes y caracteres especiales
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

st.title("📊 Analizador de Participantes")
st.write("Sube tu archivo para comparar quiénes iniciaron y terminaron.")

# Lógica de carga de archivo
uploaded_file = st.file_uploader("Elige tu archivo Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file:
    # Leer el archivo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("Archivo cargado con éxito.")
    
    # Selector de columnas (para que el usuario elija dónde están los nombres y el estado)
    col1, col2 = st.columns(2)
    with col1:
        col_nombre = st.selectbox("Selecciona la columna de NOMBRES", df.columns)
    with col2:
        col_etapa = st.selectbox("Selecciona la columna de ETAPA (Inicio/Fin)", df.columns)

    if st.button("Ejecutar Análisis"):
        # 1. Limpieza y Normalización
        df['nombre_clean'] = df[col_nombre].apply(normalizar_texto)
        
        # 2. Separar grupos (ajusta 'Inicio' y 'Fin' según tus datos)
        iniciaron = df[df[col_etapa].str.contains('inicio', case=False, na=False)]
        terminaron = df[df[col_etapa].str.contains('fin', case=False, na=False)]
        
        # 3. Comparación (Inner Join)
        completados = pd.merge(
            iniciaron[[col_nombre, 'nombre_clean']], 
            terminaron[['nombre_clean']], 
            on='nombre_clean', 
            how='inner'
        ).drop_duplicates(subset=['nombre_clean'])

        # Mostrar Resultados
        st.divider()
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Iniciaron", len(iniciaron))
        metric2.metric("Terminaron", len(terminaron))
        metric3.metric("Hicieron ambas", len(completados))

        st.subheader("Personas que completaron ambas encuestas:")
        st.dataframe(completados[col_nombre], use_container_width=True)
else:
    st.info("Esperando archivo... Por favor, sube un Excel para comenzar.")
