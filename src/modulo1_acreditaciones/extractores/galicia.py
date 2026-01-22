import pdfplumber
import pandas as pd
import logging
from .motor_base import limpiar_moneda

def extraer_galicia(ruta_pdf):
    logging.info("Iniciando motor de extracción: GALICIA")
    datos = []
    
    # Galicia suele ser más limpio, usamos tolerancia estándar
    ajustes = {
        "vertical_strategy": "text", 
        "horizontal_strategy": "text",
    }

    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            tabla = pagina.extract_table(ajustes)
            if not tabla: continue
            
            # Buscamos encabezado
            start_idx = -1
            for idx, fila in enumerate(tabla):
                fila_str = " ".join([str(x) for x in fila if x]).upper()
                if "DESCRIPCI" in fila_str and "ORIGEN" in fila_str:
                    start_idx = idx + 1
                    break
            
            filas_datos = tabla[start_idx:] if start_idx != -1 else tabla

            for fila in filas_datos:
                # Filtros de basura Galicia
                texto_fila = "".join([str(x) for x in fila if x]).upper()
                if "SALDO INICIAL" in texto_fila or "TOTALES" in texto_fila or "CONSOLIDADO" in texto_fila:
                    continue
                
                # Galicia PDF Estructura: 
                # Fecha | Descripción | Origen | Crédito | Débito | Saldo
                # Ojo: A veces Crédito y Débito cambian de lugar. Verificamos encabezado si pudiéramos, 
                # pero aquí asumiremos la estructura del PDF subido: Col 3=Credito, Col 4=Debito
                
                if len(fila) < 5: continue

                item = {
                    'Fecha': fila[0],
                    'Descripcion': f"{fila[1]} {fila[2] if fila[2] else ''}", # Unimos Desc + Origen
                    'Credito': limpiar_moneda(fila[3]), 
                    'Debito': limpiar_moneda(fila[4]),
                    'Banco': 'GALICIA'
                }

                if item['Fecha'] and '/' in str(item['Fecha']):
                    datos.append(item)

    df = pd.DataFrame(datos)
    return df