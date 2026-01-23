import os
import logging
import pandas as pd # Necesario para trucos de columnas
from src.modulo1_acreditaciones.extractor_pdf import extraer_tabla_movimientos
from src.modulo1_acreditaciones.clasificador_ia import ClasificadorMovimientos

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def normalizar_columnas(df):
    """
    Intenta adivinar cuál columna es la descripción basándose en el contenido.
    La columna de descripción suele ser la que tiene el texto más largo promedio.
    """
    columnas = df.columns.tolist()
    logging.info(f"Columnas originales detectadas: {columnas}")
    
    columna_candidata = None
    max_longitud_promedio = 0

    for col in columnas:
        # Convertimos a string y medimos longitud promedio
        try:
            longitud_promedio = df[col].astype(str).str.len().mean()
            if longitud_promedio > max_longitud_promedio:
                max_longitud_promedio = longitud_promedio
                columna_candidata = col
        except:
            continue
    
    if columna_candidata:
        logging.info(f"DETECTADO AUTOMÁTICAMENTE: La columna de descripción parece ser '{columna_candidata}'")
        # Renombramos para que el resto del código siempre use el mismo nombre
        df = df.rename(columns={columna_candidata: 'DESCRIPCION_FINAL'})
        return df, True
    else:
        return df, False

def main():
    print("=== SUITE DE FISCALIZACIÓN INTELIGENTE: V2.0 ===")
    
    # 1. Definición de rutas (Asegúrate de que el nombre del PDF coincida con el que tienes en la carpeta)
    archivo_pdf = "data/input/2024-01 CREDICOOP.pdf" 
    archivo_salida = "data/output/reporte_fiscalizacion.xlsx"
    
    if not os.path.exists(archivo_pdf):
        logging.error(f"No encuentro el archivo: {archivo_pdf}")
        return

    # 2. Extracción
    logging.info(f"Extrayendo: {archivo_pdf}...")
    df_movimientos = extraer_tabla_movimientos(archivo_pdf)
    
    if df_movimientos.empty:
        logging.error("La extracción falló (DataFrame vacío).")
        return

    # 3. Normalización (El truco nuevo)
    df_movimientos, exito = normalizar_columnas(df_movimientos)
    
    if not exito:
        logging.error("No pudimos detectar automáticamente la columna de descripción.")
        return
    '''
    # 4. Clasificación con IA
    # Ahora siempre usamos 'DESCRIPCION_FINAL', no importa si el banco le llama 'Concepto' o 'Detalle'
    clasificador = ClasificadorMovimientos()
    df_final = clasificador.clasificar_dataframe(df_movimientos, 'DESCRIPCION_FINAL')
    '''
    # 5. Guardado
    df_final.to_excel(archivo_salida, index=False)
    logging.info(f"¡ÉXITO! Reporte guardado en: {archivo_salida}")

if __name__ == "__main__":
    main()