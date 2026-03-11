import streamlit as st
import pandas as pd
import unicodedata

# Configuración de la interfaz de usuario
st.set_page_config(
    page_title="Validador de Participantes",
    page_icon="✅",
    layout="wide"
)

def normalizar_nombre(texto):
    """
    Limpia el texto: quita tildes, convierte a minúsculas y elimina espacios extra.
    Ejemplo: 'Ángel ' -> 'angel'
    """
    if not isinstance(texto, str):
        return ""
    # Convertir a minúsculas y quitar espacios en los extremos
    texto = texto.strip().lower()
    # Normalización para eliminar acentos/tildes
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

st.title("📊 Comparador de Bases de Datos con Índice")
st.markdown("""
Esta herramienta identifica quiénes completaron ambas encuestas y te indica **en qué fila del archivo original** se encuentra cada persona.
""")

# Layout para subir archivos
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Archivo de Inicio")
    file_inicio = st.file_uploader("Subir base de quienes iniciaron", type=['xlsx', 'csv'], key="inicio_upload")

with col2:
    st.subheader("2. Archivo de Fin")
    file_fin = st.file_uploader("Subir base de quienes terminaron", type=['xlsx', 'csv'], key="fin_upload")

if file_inicio and file_fin:
    # Cargar los archivos
    try:
        if file_inicio.name.endswith('.xlsx'):
            df_i = pd.read_excel(file_inicio)
        else:
            df_i = pd.read_csv(file_inicio)
            
        if file_fin.name.endswith('.xlsx'):
            df_f = pd.read_excel(file_fin)
        else:
            df_f = pd.read_csv(file_fin)
            
        st.success("Archivos cargados correctamente.")
    except Exception as e:
        st.error(f"Error al leer los archivos: {e}")
        st.stop()

    st.divider()
    
    # Selección de columnas para comparar
    st.subheader("Configuración de columnas")
    c1, c2 = st.columns(2)
    
    with c1:
        col_nombre_i = st.selectbox("Columna de Nombre en archivo Inicio", df_i.columns)
    with c2:
        col_nombre_f = st.selectbox("Columna de Nombre en archivo Fin", df_f.columns)

    if st.button("🔍 Iniciar Comparación"):
        # Crear copias para no alterar los datos originales
        df_i_work = df_i.copy()
        df_f_work = df_f.copy()

        # Capturar el número de fila original (Excel: índice + 2, asumiendo encabezado en fila 1)
        df_i_work['fila_origen'] = df_i_work.index + 2

        # Generar llave de comparación limpia
        df_i_work['key_clean'] = df_i_work[col_nombre_i].astype(str).apply(normalizar_nombre)
        df_f_work['key_clean'] = df_f_work[col_nombre_f].astype(str).apply(normalizar_nombre)

        # Realizar el cruce (Inner Join)
        # Incluimos 'fila_origen' en la selección de columnas de la izquierda
        coincidencias = pd.merge(
            df_i_work[[col_nombre_i, 'key_clean', 'fila_origen']], 
            df_f_work[['key_clean']], 
            on='key_clean', 
            how='inner'
        ).drop_duplicates(subset=['key_clean'])

        # Mostrar resultados
        st.divider()
        if not coincidencias.empty:
            st.balloons()
            st.success(f"¡Se encontraron {len(coincidencias)} personas que realizaron ambas encuestas!")
            
            # Crear DataFrame final ordenado y limpio
            df_final = pd.DataFrame()
            df_final["Fila en Origen (Excel)"] = coincidencias['fila_origen'].values
            df_final["Nombre Completo"] = coincidencias[col_nombre_i].values
            
            # Ordenar por fila para facilitar la revisión
            df_final = df_final.sort_values(by="Fila en Origen (Excel)")
            
            st.subheader("Resultados de la comparación:")
            st.dataframe(df_final, use_container_width=True, hide_index=True)
            
            # Botón de descarga con codificación para Excel
            csv_output = df_final.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 Descargar Reporte con Filas (CSV)",
                data=csv_output,
                file_name="coincidencias_con_indices.csv",
                mime="text/csv"
            )
        else:
            st.warning("No se encontraron coincidencias. Verifica las columnas seleccionadas.")
else:
    st.info("💡 Sube ambos archivos para habilitar la herramienta de comparación.")
