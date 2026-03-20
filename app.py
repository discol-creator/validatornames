import streamlit as st
import pandas as pd
import unicodedata
from thefuzz import fuzz, process

# Configuración de la interfaz
st.set_page_config(
    page_title="Validador Pro - Comparación Flexible",
    page_icon="🔍",
    layout="wide"
)

def normalizar_nombre(texto):
    """Limpia texto: minúsculas, sin tildes, sin espacios extra."""
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

st.title("📊 Validador de Participantes Inteligente")
st.markdown("""
Esta versión incluye **Comparación Flexible**. Puede identificar personas aunque hayan escrito su nombre ligeramente diferente 
(ej: "Rosa Pérez" vs "Rosalba Pérez"), analizando la similitud entre los textos.
""")

# Carga de archivos
col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Archivo de Inicio")
    file_inicio = st.file_uploader("Subir base de INICIO", type=['xlsx', 'csv'], key="in_up")
with col2:
    st.subheader("2. Archivo de Fin")
    file_fin = st.file_uploader("Subir base de FIN", type=['xlsx', 'csv'], key="fin_up")

if file_inicio and file_fin:
    try:
        df_i = pd.read_excel(file_inicio) if file_inicio.name.endswith('.xlsx') else pd.read_csv(file_inicio)
        df_f = pd.read_excel(file_fin) if file_fin.name.endswith('.xlsx') else pd.read_csv(file_fin)
        st.success("Archivos cargados correctamente.")
    except Exception as e:
        st.error(f"Error al leer archivos: {e}")
        st.stop()

    st.divider()
    
    # Configuración de columnas
    st.subheader("⚙️ Configuración del Análisis")
    c1, c2, c3 = st.columns([2, 2, 1])
    
    with c1:
        cols_i = st.multiselect("Columnas de Identidad (Inicio)", df_i.columns, help="Selecciona Nombre y Apellidos")
    with c2:
        cols_f = st.multiselect("Columnas de Identidad (Fin)", df_f.columns, help="Selecciona Nombre y Apellidos")
    with c3:
        modo = st.radio("Modo de cruce", ["Exacto", "Flexible (Fuzzy)"])
        if modo == "Flexible (Fuzzy)":
            umbral = st.slider("Nivel de similitud", 60, 100, 85, help="85 es recomendado. Valores más bajos aceptan más diferencias.")

    if st.button("🚀 Iniciar Análisis"):
        if not cols_i or not cols_f:
            st.warning("Selecciona las columnas de nombre/apellido en ambos archivos.")
        else:
            # Preparar datos
            df_i_work = df_i.copy()
            df_f_work = df_f.copy()
            
            df_i_work['fila_original'] = df_i_work.index + 2
            df_i_work['full_display'] = df_i_work[cols_i].astype(str).agg(' '.join, axis=1)
            df_f_work['full_display'] = df_f_work[cols_f].astype(str).agg(' '.join, axis=1)
            
            # Normalizar para comparación
            df_i_work['clean'] = df_i_work['full_display'].apply(normalizar_nombre)
            df_f_work['clean'] = df_f_work['full_display'].apply(normalizar_nombre)

            lista_matches = []

            if modo == "Exacto":
                # Lógica de unión exacta (la que ya teníamos)
                coincidencias = pd.merge(
                    df_i_work, df_f_work[['clean']], on='clean', how='inner'
                ).drop_duplicates(subset=['clean'])
                
                for _, row in coincidencias.iterrows():
                    lista_matches.append({
                        "Fila Inicio": row['fila_original'],
                        "Participante": row['full_display'],
                        "Similitud": "100% (Exacto)"
                    })
            else:
                # Lógica Flexible (Fuzzy Matching)
                progress_bar = st.progress(0)
                nombres_fin = df_f_work['clean'].unique().tolist()
                
                total = len(df_i_work)
                for i, (idx, row) in enumerate(df_i_work.iterrows()):
                    nombre_buscar = row['clean']
                    # Encontrar el mejor match en el archivo de Fin
                    mejor_match, score = process.extractOne(nombre_buscar, nombres_fin, scorer=fuzz.token_sort_ratio)
                    
                    if score >= umbral:
                        lista_matches.append({
                            "Fila Inicio": row['fila_original'],
                            "Participante": row['full_display'],
                            "Similitud": f"{score}%"
                        })
                    
                    # Actualizar progreso cada 10 registros
                    if i % 10 == 0:
                        progress_bar.progress((i + 1) / total)
                progress_bar.empty()

            # Mostrar resultados
            st.divider()
            if lista_matches:
                df_res = pd.DataFrame(lista_matches).drop_duplicates(subset=['Participante'])
                st.balloons()
                st.success(f"Se encontraron {len(df_res)} coincidencias.")
                
                st.dataframe(df_res, use_container_width=True, hide_index=True)
                
                csv = df_res.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Descargar Reporte de Coincidencias", csv, "coincidencias_inteligentes.csv", "text/csv")
            else:
                st.warning("No se encontraron coincidencias con los parámetros seleccionados.")
else:
    st.info("💡 Sube ambos archivos para comenzar el análisis inteligente.")
