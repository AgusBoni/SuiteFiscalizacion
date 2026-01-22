# src/modulo1_acreditaciones/extractor_pdf.py
import pdfplumber
import pandas as pd
import logging

def extraer_tabla_movimientos(ruta_pdf):
    """
    Abre un PDF, detecta tablas en todas sus páginas y las une en un solo DataFrame.
    """
    datos_totales = []
    
    try:
        # 'with' es un Context Manager: abre y cierra el archivo automáticamente (seguridad)
        with pdfplumber.open(ruta_pdf) as pdf:
            logging.info(f"Procesando PDF con {len(pdf.pages)} páginas.")
            
            for i, pagina in enumerate(pdf.pages):
                # extract_table() busca líneas verticales y horizontales para definir celdas
                tabla = pagina.extract_table()
                
                if tabla:
                    # Si es la primera página, incluimos los encabezados (fila 0)
                    # Si es la página 2, 3, etc., saltamos el encabezado para no repetirlo
                    if i == 0:
                        datos_totales.extend(tabla)
                    else:
                        # Asumimos que el encabezado se repite, lo saltamos (slice [1:])
                        datos_totales.extend(tabla[1:])
                else:
                    logging.warning(f"No se detectaron tablas en la página {i+1}")

        if not datos_totales:
            raise ValueError("El PDF no contenía tablas legibles.")

        # Convertimos la lista de listas en un DataFrame de Pandas
        # La primera fila (índice 0) son las columnas
        df = pd.DataFrame(datos_totales[1:], columns=datos_totales[0])
        return df

    except Exception as e:
        logging.error(f"Error crítico extrayendo PDF: {e}")
        return pd.DataFrame() # Retornamos vacío en caso de error para no romper el flujo