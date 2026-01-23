import os
import logging
import pandas as pd
from src.modulo1_acreditaciones import extractor_pdf

# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    print("\n=== SUITE DE FISCALIZACIÓN: MODO SOLO EXTRACCIÓN ===")
    
    # RUTAS
    archivo_pdf = "data/input/2024-01 CREDICOOP.pdf"
    archivo_salida = "data/output/reporte_base_sin_clasificar.xlsx"

    if not os.path.exists(archivo_pdf):
        logging.error(f"❌ No encuentro el archivo: {archivo_pdf}")
        return

    # 1. EXTRACCIÓN
    logging.info(f"📂 Leyendo PDF: {archivo_pdf}...")
    try:
        df_movimientos = extractor_pdf.extraer_tabla_movimientos(archivo_pdf)
    except Exception as e:
        logging.error(f"❌ Error al leer PDF: {e}")
        return

    if df_movimientos is None or df_movimientos.empty:
        logging.error("❌ El PDF se leyó pero no salieron datos (Tabla vacía).")
        return

    # 2. PRUEBA DE FUEGO (SUMAS DE CONTROL)
    total_creditos = df_movimientos['Credito'].sum()
    total_debitos = df_movimientos['Debito'].sum()
    count_filas = len(df_movimientos)

    print("\n" + "="*50)
    print(f"📊 REPORTE DE EXTRACCIÓN (Verificar contra PDF)")
    print("="*50)
    print(f"✅ Filas Extraídas:      {count_filas}")
    print(f"💰 TOTAL CRÉDITOS (Entradas): $ {total_creditos:,.2f}")
    print(f"💸 TOTAL DÉBITOS (Salidas):   $ {total_debitos:,.2f}")
    print("="*50 + "\n")

    # Verificación de Ceros
    if total_creditos == 0 and total_debitos == 0:
        logging.critical("🚨 ¡ALERTA! Los montos siguen en CERO. Revisa 'motor_base.py'.")
    else:
        logging.info("✅ Los montos parecen correctos (distintos de cero).")

    # 3. GUARDADO (SIN IA)
    # Comentamos la IA como pediste
    # df_final = clasificador.clasificar(...) 
    
    logging.info(f"💾 Guardando Excel base en: {archivo_salida}")
    df_movimientos.to_excel(archivo_salida, index=False)
    print("🚀 Listo para clasificación manual.")

if __name__ == "__main__":
    main()