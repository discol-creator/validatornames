import pandas as pd
import unicodedata

# Configuración de la página
st.set_page_config(page_title="Comparador de Encuestas", layout="wide")
# Configuración de página
st.set_page_config(page_title="Comparador de Dos Archivos", layout="wide")

def normalizar_texto(texto):
    """Limpia el texto: minúsculas, sin tildes y sin espacios extra."""
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
st.title("🔄 Comparador de Dos Bases de Datos")
st.markdown("Sube los dos archivos para encontrar a las personas que aparecen en ambos (ignorando tildes y mayúsculas).")

# Lógica de carga de archivo
uploaded_file = st.file_uploader("Elige tu archivo Excel o CSV", type=['xlsx', 'csv'])
# Layout de dos columnas para subir archivos
col_a, col_b = st.columns(2)

if uploaded_file:
    # Leer el archivo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
with col_a:
    st.subheader("1. Base de Inicio")
    file_inicio = st.file_uploader("Archivo de quienes iniciaron", type=['xlsx', 'csv'], key="inicio")

    st.success("Archivo cargado con éxito.")
with col_b:
    st.subheader("2. Base de Fin")
    file_fin = st.file_uploader("Archivo de quienes terminaron", type=['xlsx', 'csv'], key="fin")

if file_inicio and file_fin:
    # Cargar datos
    df_inicio = pd.read_excel(file_inicio) if file_inicio.name.endswith('.xlsx') else pd.read_csv(file_inicio)
    df_fin = pd.read_excel(file_fin) if file_fin.name.endswith('.xlsx') else pd.read_csv(file_fin)
    
    st.divider()

    # Selector de columnas (para que el usuario elija dónde están los nombres y el estado)
    col1, col2 = st.columns(2)
    with col1:
        col_nombre = st.selectbox("Selecciona la columna de NOMBRES", df.columns)
    with col2:
        col_etapa = st.selectbox("Selecciona la columna de ETAPA (Inicio/Fin)", df.columns)
    # Selección de columnas de nombre en cada archivo
    c1, c2 = st.columns(2)
    with c1:
        col_nombre_inicio = st.selectbox("Columna de nombre (Inicio)", df_inicio.columns)
    with c2:
        col_nombre_fin = st.selectbox("Columna de nombre (Fin)", df_fin.columns)

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

        # Mostrar Resultados
        st.divider()
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Iniciaron", len(iniciaron))
        metric2.metric("Terminaron", len(terminaron))
        metric3.metric("Hicieron ambas", len(completados))
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

        st.subheader("Personas que completaron ambas encuestas:")
        st.dataframe(completados[col_nombre], use_container_width=True)
else:
    st.info("Esperando archivo... Por favor, sube un Excel para comenzar.")
    st.info("Por favor, sube ambos archivos para habilitar la comparación.")
