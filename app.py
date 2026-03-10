import streamlit as st
import pandas as pd
import unicodedata

# Configuración de página
st.set_page_config(page_title="Comparador de Dos Archivos", layout="wide")

def normalizar_texto(texto):
    """Limpia el texto: minúsculas, sin tildes y sin espacios extra."""
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

st.title("🔄 Comparador de Dos Bases de Datos")
st.markdown("Sube los dos archivos para encontrar a las personas que aparecen en ambos (ignorando tildes y mayúsculas).")

# Layout de dos columnas para subir archivos
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("1. Base de Inicio")
    file_inicio = st.file_uploader("Archivo de quienes iniciaron", type=['xlsx', 'csv'], key="inicio")

with col_b:
    st.subheader("2. Base de Fin")
    file_fin = st.file_uploader("Archivo de quienes terminaron", type=['xlsx', 'csv'], key="fin")

if file_inicio and file_fin:
    # Cargar datos
    df_inicio = pd.read_excel(file_inicio) if file_inicio.name.endswith('.xlsx') else pd.read_csv(file_inicio)
    df_fin = pd.read_excel(file_fin) if file_fin.name.endswith('.xlsx') else pd.read_csv(file_fin)
    
    st.divider()
    
    # Selección de columnas de nombre en cada archivo
    c1, c2 = st.columns(2)
    with c1:
        col_nombre_inicio = st.selectbox("Columna de nombre (Inicio)", df_inicio.columns)
    with c2:
        col_nombre_fin = st.selectbox("Columna de nombre (Fin)", df_fin.columns)

    if st.button("🔍 Comparar Bases de Datos"):
        # Normalización
        df_inicio['nombre_clean'] = df_inicio[col_nombre_inicio].apply(normalizar_texto)
        df_fin['nombre_clean'] = df_fin[col_nombre_fin].apply(normalizar_texto)

        # Cruce de datos (Inner Join)
        coincidencias = pd.merge(
            df_inicio[[col_nombre_inicio, 'nombre_clean']], 
            df_fin[[col_nombre_fin, 'nombre_clean']], 
            on='nombre_clean', 
            how='inner'
        ).drop_duplicates(subset=['nombre_clean'])

        # Resultados
        st.success(f"¡Análisis completado! Se encontraron {len(coincidencias)} personas en ambos archivos.")
        
        # Mostrar tabla de resultados
        st.subheader("Lista de personas que completaron el proceso:")
        # Renombrar para mayor claridad en la tabla final
        resultado_final = coincidencias[[col_nombre_inicio]].rename(columns={col_nombre_inicio: "Nombre Identificado"})
        st.dataframe(resultado_final, use_container_width=True)
        
        # Opción para descargar el resultado
        csv = resultado_final.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar lista en CSV", csv, "coincidencias.csv", "text/csv")

else:
    st.info("Por favor, sube ambos archivos para habilitar la comparación.")
