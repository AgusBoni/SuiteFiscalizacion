import pdfplumber
import pandas as pd
import logging
from .motor_base import limpiar_moneda

def extraer_credicoop(ruta_pdf):
    logging.info("Iniciando motor de extracción: CREDICOOP")
    datos = []
    
    # Ajustes calibrados para tu PDF de Credicoop
    # x_tolerance=15 permite que textos separados por espacios cortos se unan
    ajustes = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 4,
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        for i, pagina in enumerate(pdf.pages):
            tabla = pagina.extract_table(ajustes)
            
            if not tabla: continue
            
            # Limpiamos filas vacías
            tabla = [fila for fila in tabla if fila and any(fila)]
            
            # Estrategia de Encabezados:
            # Buscamos la fila que contiene "DESCRIPCION" para saber dónde empiezan los datos
            start_idx = -1
            for idx, fila in enumerate(tabla):
                # Unimos la fila en un texto para buscar la palabra clave
                fila_str = " ".join([str(x) for x in fila if x]).upper()
                if "DESCRIPCION" in fila_str and "FECHA" in fila_str:
                    start_idx = idx + 1 # Los datos empiezan en la siguiente
                    break
            
            if start_idx != -1:
                # Si encontramos encabezado, tomamos desde ahí hacia abajo
                filas_datos = tabla[start_idx:]
            else:
                # Si no hay encabezado (páginas siguientes), tomamos todo
                # PERO cuidado con filas de "Saldo al..." o "Viene de..."
                filas_datos = tabla

            for fila in filas_datos:
                # El PDF Credicoop tiene 6 columnas aprox.
                # FECHA | COMBTE | DESCRIPCION | DEBITO | CREDITO | SALDO
                # A veces pdfplumber lee menos columnas si están vacías.
                
                # Descartamos filas basura (ej: "VIENE DE PAGINA...")
                texto_fila = "".join([str(x) for x in fila if x])
                if "VIENE DE" in texto_fila or "CONTINUA EN" in texto_fila or "SALDO AL" in texto_fila:
                    continue
                
                # Normalización de longitud (Rellenamos con None si faltan columnas)
                while len(fila) < 6:
                    fila.append(None)
                
                # Mapeo específico según tu PDF
                item = {
                    'Fecha': fila[0],
                    'Descripcion': fila[2], # Columna C
                    'Debito': limpiar_moneda(fila[3]), # Columna D
                    'Credito': limpiar_moneda(fila[4]), # Columna E
                    'Banco': 'CREDICOOP'
                }
                
                # Solo agregamos si hay fecha válida (filtro simple)
                if item['Fecha'] and '/' in str(item['Fecha']):
                    datos.append(item)

    df = pd.DataFrame(datos)
    return df