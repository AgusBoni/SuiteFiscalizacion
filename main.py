import os
import logging
from src.modulo1_acreditaciones import extractor_pdf
from src.modulo1_acreditaciones.clasificador_reglas import ClasificadorReglas # Usamos el nuevo script

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    print("=== SUITE DE FISCALIZACIÓN: MODO TURBO (REGLAS) ===")
    
    archivo_pdf = "data/input/2024-01 CREDICOOP.pdf"
    archivo_salida = "data/output/reporte_fiscalizacion_final.xlsx"

    # 1. EXTRACCIÓN
    logging.info(f"📂 Extrayendo datos de: {archivo_pdf}...")
    df = extractor_pdf.extraer_tabla_movimientos(archivo_pdf)
    
    if df is None or df.empty:
        logging.error("❌ No se extrajeron datos.")
        return

    # 2. CLASIFICACIÓN (LOGICA)
    logging.info("🧠 Clasificando movimientos por Reglas (Sin API)...")
    clasificador = ClasificadorReglas()
    df_clasificado = clasificador.clasificar(df)

    # 3. EXPORTACIÓN
    logging.info(f"💾 Guardando reporte en: {archivo_salida}")
    df_clasificado.to_excel(archivo_salida, index=False)
    
    # 4. RESUMEN RAPIDO
    ventas = df_clasificado[df_clasificado['Categoria_IA'] == 'VENTA']['Credito'].sum()
    print("\n" + "="*40)
    print("✅ ¡PROCESO TERMINADO EN SEGUNDOS!")
    print(f"💰 Total Ventas Detectadas: $ {ventas:,.2f}")
    print("="*40)

if __name__ == "__main__":
    main()