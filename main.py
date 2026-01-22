import os
import logging
from src.modulo1_acreditaciones.extractor_pdf import extraer_tabla_movimientos
from src.modulo1_acreditaciones.clasificador_ia import ClasificadorMovimientos

# Configuración global de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    print("=== SUITE DE FISCALIZACIÓN INTELIGENTE: INICIO ===")
    
    # 1. Definición de rutas
    archivo_pdf = "data/input/2024-01 CREDICOOP.pdf" # ¡Asegúrate de poner un PDF aquí!
    archivo_salida = "data/output/reporte_fiscalizacion.xlsx"
    
    # Verificación de existencia
    if not os.path.exists(archivo_pdf):
        logging.error(f"No se encuentra el archivo: {archivo_pdf}")
        return

    # 2. Extracción (Módulo Extractor)
    logging.info(f"Paso 1: Extrayendo datos de {archivo_pdf}...")
    try:
        df_movimientos = extraer_tabla_movimientos(archivo_pdf)
        logging.info(f"Extracción exitosa. Filas detectadas: {len(df_movimientos)}")
    except Exception as e:
        logging.critical(f"No se pudo extraer el PDF: {e}")
        return
    
    # AGREGA ESTO TEMPORALMENTE:
    print("COLUMNAS DETECTADAS:", df_movimientos.columns.tolist()) 
    # Esto imprimirá algo como: ['Fecha', 'Descripción\nOperación', 'Importe']

    # 3. Clasificación (Módulo IA)
    # IMPORTANTE: Busca cuál es el nombre real de la columna en TU pdf.
    # A veces es "Descripción", "Concepto", "Detalle". Cámbialo aquí abajo.
    columna_concepto = "DESCRIPCION" 
    
    if columna_concepto not in df_movimientos.columns:
        logging.error(f"Columna '{columna_concepto}' no encontrada. Columnas disponibles: {df_movimientos.columns.tolist()}")
        return

    logging.info("Paso 2: Consultando a Gemini (IA)...")
    clasificador = ClasificadorMovimientos()
    df_final = clasificador.clasificar_dataframe(df_movimientos, columna_concepto)

    # 4. Generación de Reporte (Salida)
    logging.info(f"Paso 3: Guardando reporte en {archivo_salida}...")
    try:
        # index=False evita que se guarde el número de fila (0, 1, 2...)
        df_final.to_excel(archivo_salida, index=False)
        logging.info("=== PROCESO TERMINADO CON ÉXITO ===")
        logging.info(f"Por favor revisa la carpeta: {archivo_salida}")
    except Exception as e:
        logging.error(f"Error guardando el Excel: {e}")

if __name__ == "__main__":
    main()