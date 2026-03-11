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

st.title("📊 Comparador de Participantes (Nombre y Apellido)")
st.markdown("""
Esta herramienta identifica quiénes completaron ambas encuestas uniendo las columnas que selecciones (como Nombre y Apellido).
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
    st.subheader("Configuración de Identidad")
    st.info("Selecciona las columnas que forman el nombre completo (ej: Nombre y luego Apellido). El orden en que las selecciones es como aparecerán.")
    
    c1, c2 = st.columns(2)
    
    with c1:
        cols_i = st.multiselect("Columnas de Identidad (Inicio)", df_i.columns, help="Selecciona 'Nombre' y 'Apellido'")
    with c2:
        cols_f = st.multiselect("Columnas de Identidad (Fin)", df_f.columns, help="Selecciona 'Nombre' y 'Apellido'")

    if st.button("🔍 Iniciar Comparación"):
        if not cols_i or not cols_f:
            st.warning("Por favor, selecciona al menos una columna en cada archivo para identificar a las personas.")
        else:
            # Crear copias para no alterar los datos originales
            df_i_work = df_i.copy()
            df_f_work = df_f.copy()

            # Capturar el número de fila original (Excel: índice + 2)
            df_i_work['fila_origen'] = df_i_work.index + 2

            # Combinar las columnas seleccionadas en una sola cadena de texto
            # Ejemplo: "Juan" + " " + "Perez" -> "Juan Perez"
            df_i_work['full_name_display'] = df_i_work[cols_i].astype(str).agg(' '.join, axis=1)
            df_f_work['full_name_display'] = df_f_work[cols_f].astype(str).agg(' '.join, axis=1)

            # Generar llave de comparación limpia basada en el nombre completo unido
            df_i_work['key_clean'] = df_i_work['full_name_display'].apply(normalizar_nombre)
            df_f_work['key_clean'] = df_f_work['full_name_display'].apply(normalizar_nombre)

            # Realizar el cruce (Inner Join)
            coincidencias = pd.merge(
                df_i_work[['full_name_display', 'key_clean', 'fila_origen']], 
                df_f_work[['key_clean']], 
                on='key_clean', 
                how='inner'
            ).drop_duplicates(subset=['key_clean'])

            # Mostrar resultados
            st.divider()
            if not coincidencias.empty:
                st.balloons()
                st.success(f"¡Se encontraron {len(coincidencias)} personas que realizaron ambas encuestas!")
                
                # Crear DataFrame final ordenado
                df_final = pd.DataFrame()
                df_final["Fila en Origen (Excel)"] = coincidencias['fila_origen'].values
                df_final["Participante (Nombre y Apellido)"] = coincidencias['full_name_display'].values
                
                # Ordenar por fila
                df_final = df_final.sort_values(by="Fila en Origen (Excel)")
                
                st.subheader("Resultados de la comparación:")
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                
                # Botón de descarga
                csv_output = df_final.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Descargar Reporte Completo (CSV)",
                    data=csv_output,
                    file_name="coincidencias_completas.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No se encontraron coincidencias. Asegúrate de haber seleccionado las columnas equivalentes en ambos archivos.")
else:
    st.info("💡 Sube ambos archivos para configurar las columnas de Nombre y Apellido.")
