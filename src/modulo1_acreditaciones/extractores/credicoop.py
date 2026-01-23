import pdfplumber
import pandas as pd
from decimal import Decimal
from src.modulo1_acreditaciones.extractores.motor_base import limpiar_moneda # Usamos la función arreglada

def extraer_credicoop(pdf_path):
    """
    Extractor específico para CREDICOOP (Versión Robustecida)
    """
    data = []
    
    # Configuración para leer tablas sin bordes (ajustable si falla)
    ajustes_tabla = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "snap_tolerance": 4,
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extraemos tabla
            table = page.extract_table(ajustes_tabla)
            
            if table:
                for row in table:
                    # Filtramos filas vacías o muy cortas
                    if not row or len(row) < 4:
                        continue
                    
                    # Limpieza básica de Nones
                    row = [elem if elem else "" for elem in row]
                    
                    # Lógica de detección de columnas (según PDF estándar de Credicoop)
                    # Usualmente: Fecha [0], Concepto [1], Comprobante [2], Debito [3], Credito [4], Saldo [5]
                    # A veces varía, pero buscamos patrones de fecha
                    fecha = row[0]
                    
                    # Si la fecha parece fecha (dd/mm/aa)
                    if "/" in str(fecha) and len(str(fecha)) <= 10:
                        descripcion = row[1] + " " + row[2] # Unimos concepto y comprobante
                        val_1 = limpiar_moneda(row[3])
                        val_2 = limpiar_moneda(row[4])

                        # Analizamos la descripción para saber dónde poner la plata
                        desc_lower = descripcion.lower()
                        palabras_debito = ['impuesto', 'ley 25.413', 'iva', 'debito', 'pago', 'comision', 'extraccion', 'suscripcion', 'retencion', 'i.b.', 'sircreb']

                        # Si la descripción suena a gasto, forzamos que vaya a Débito
                        if any(p in desc_lower for p in palabras_debito):
                            debito = max(val_1, val_2) # Ponemos el valor aquí
                            credito = Decimal("0.00")
                        else:
                            # Si no es gasto obvio, confiamos en la columna original (o ajustamos según necesites)
                            # En tu caso, parece que TODO está cayendo en val_2 (row[4]), así que hay que tener cuidado.
                            # Si val_1 es 0 y val_2 tiene dato, asumimos que es Crédito salvo que la descripción diga lo contrario.
                            debito = val_1
                            credito = val_2
                        
                        # Solo agregamos si hay movimiento de dinero
                        if debito > 0 or credito > 0:
                            data.append({
                                "Fecha": fecha,
                                "DESCRIPCION_FINAL": descripcion.strip(),
                                "Debito": debito,
                                "Credito": credito,
                                "Banco": "CREDICOOP"
                            })

    df = pd.DataFrame(data)
    return df