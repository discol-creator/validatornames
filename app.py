import pandas as pd
import unicodedata

def normalizar_texto(texto):
    """Elimina tildes, convierte a minúsculas y quita espacios extra."""
    if not isinstance(texto, str):
        return ""
    # Convertir a minúsculas y quitar espacios en los extremos
    texto = texto.strip().lower()
    # Eliminar acentos/tildes
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def analizar_encuestas(archivo_path):
    # 1. Cargar la base de datos (asumiendo Excel o CSV)
    df = pd.read_excel(archivo_path) # Cambiar a pd.read_csv si es necesario
    
    # Supongamos que las columnas se llaman 'Nombre' y 'Estado' (Inicio/Fin)
    # O que tienes dos archivos/hojas separadas. 
    # Aquí simularemos que filtramos una sola lista por una columna de control.
    
    iniciaron = df[df['etapa'] == 'Inicio'].copy()
    terminaron = df[df['etapa'] == 'Fin'].copy()

    # 2. Crear columna de comparación normalizada
    iniciaron['nombre_clean'] = iniciaron['nombre_columna'].apply(normalizar_texto)
    terminaron['nombre_clean'] = terminaron['nombre_columna'].apply(normalizar_texto)

    # 3. Comparar (Inner Join) para encontrar quienes están en ambas
    lograron_ambas = pd.merge(
        iniciaron[['nombre_columna', 'nombre_clean']], 
        terminaron[['nombre_clean']], 
        on='nombre_clean', 
        how='inner'
    ).drop_duplicates(subset=['nombre_clean'])

    print(f"Total iniciaron: {len(iniciaron)}")
    print(f"Total terminaron: {len(terminaron)}")
    print(f"Completaron ambas: {len(lograron_ambas)}")
    
    return lograron_ambas['nombre_columna']

# Ejecución
# resultado = analizar_encuestas('tu_base_de_datos.xlsx')
# print(resultado)