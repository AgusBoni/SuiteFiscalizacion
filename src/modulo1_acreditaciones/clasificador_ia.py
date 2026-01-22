# src/modulo1_acreditaciones/clasificador_ia.py
import logging
import time

# En el futuro importaremos: import google.generativeai as genai

class ClasificadorMovimientos:
    def __init__(self):
        # Aquí configuraremos la API Key más adelante
        pass

    def consultar_inteligencia_artificial(self, descripcion_movimiento):
        """
        Envía una descripción a la IA y retorna la categoría.
        """
        # 1. Definimos el Prompt (La instrucción estricta para la IA)
        prompt_sistema = f"""
        Actúa como un Auditor Fiscal experto. 
        Analiza el siguiente texto de un extracto bancario: '{descripcion_movimiento}'.
        Responde SOLO con una de estas etiquetas:
        - VENTA (Si es cobro de clientes, depósito, tarjeta de crédito)
        - NO_COMPUTABLE (Si es préstamo, transferencia propia, plazo fijo, reversión)
        - DUDA (Si no estás 100% seguro)
        """

        # 2. Simulación de la llamada a la API (Mocking)
        # Esto es lo que haremos realmente cuando conectemos tu API Key
        logging.info(f"Consultando IA para: {descripcion_movimiento}...")
        
        # --- SIMULACIÓN DE RESPUESTA DE GEMINI ---
        descripcion_lower = descripcion_movimiento.lower()
        if "prestamo" in descripcion_lower or "transferencia misma cuenta" in descripcion_lower:
            respuesta_simulada = "NO_COMPUTABLE"
        elif "acreditacion ventas" in descripcion_lower or "cobro" in descripcion_lower:
            respuesta_simulada = "VENTA"
        else:
            respuesta_simulada = "DUDA"
        # -----------------------------------------
        
        return respuesta_simulada

    def clasificar_dataframe(self, df, columna_descripcion):
        """
        Recorre el DataFrame y crea una nueva columna con la clasificación.
        """
        logging.info("Iniciando clasificación inteligente de movimientos...")
        
        # Creamos la columna vacía
        df['Categoria_IA'] = ''

        # Iteramos fila por fila (Iterrows es lento, pero seguro para principiantes y debug)
        for index, fila in df.iterrows():
            descripcion = fila[columna_descripcion]
            
            # Llamamos a la "IA"
            categoria = self.consultar_inteligencia_artificial(descripcion)
            
            # Guardamos el resultado
            df.at[index, 'Categoria_IA'] = categoria
            
        return df