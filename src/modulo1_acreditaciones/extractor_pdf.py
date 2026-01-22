import pdfplumber
import logging
import pandas as pd
from .extractores.credicoop import extraer_credicoop
from .extractores.galicia import extraer_galicia

def detectar_banco(ruta_pdf):
    """
    Abre la primera página y busca palabras clave para decidir la estrategia.
    """
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            if not pdf.pages: return None
            # Leemos solo la primera página para ser rápidos
            texto_portada = pdf.pages[0].extract_text().upper()
            
            if "CREDICOOP" in texto_portada:
                return "CREDICOOP"
            elif "GALICIA" in texto_portada:
                return "GALICIA"
            else:
                return "DESCONOCIDO"
    except Exception as e:
        logging.error(f"Error detectando banco: {e}")
        return None

def extraer_tabla_movimientos(ruta_pdf):
    """
    Función principal llamada desde main.py
    """
    banco = detectar_banco(ruta_pdf)
    
    if banco == "CREDICOOP":
        df = extraer_credicoop(ruta_pdf)
    elif banco == "GALICIA":
        df = extraer_galicia(ruta_pdf)
    else:
        logging.error(f"No se detectó un banco compatible para {ruta_pdf}")
        return pd.DataFrame() # Devuelve vacío si falla

    # --- FASE DE INTEGRIDAD (CHECKSUM) ---
    if not df.empty:
        total_creditos = df['Credito'].sum()
        total_debitos = df['Debito'].sum()
        logging.info(f"--- SUMAS DE CONTROL ({banco}) ---")
        logging.info(f"Total Créditos detectados: $ {total_creditos}")
        logging.info(f"Total Débitos detectados:  $ {total_debitos}")
        
        # Normalización final de columnas para que coincida con lo que espera el clasificador IA
        # El clasificador espera 'DESCRIPCION_FINAL'
        df = df.rename(columns={'Descripcion': 'DESCRIPCION_FINAL'})
        
    return df