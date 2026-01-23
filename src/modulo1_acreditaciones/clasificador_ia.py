import os
import logging
import time
import pandas as pd
from google import genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ClasificadorMovimientos:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR CRÍTICO: No se encontró la GEMINI_API_KEY en el archivo .env")
        
        try:
            self.client = genai.Client(api_key=api_key)
            # Usamos Flash Latest para mejor balance de cuota/velocidad
            self.model_name = "gemini-2.0-flash" 
        except Exception as e:
            logging.error(f"Error configurando cliente Gemini: {e}")
            raise

    def generar_prompt_lote(self, df_chunk):
        """
        Convierte un trozo del DataFrame en un string optimizado para tokens.
        """
        texto_lote = ""
        # Iteramos usando el índice original para mantener referencia si fuera necesario
        for idx, fila in df_chunk.iterrows():
            # Limpiamos caracteres raros que puedan confundir al prompt
            desc = str(fila.get('DESCRIPCION_FINAL', 'Sin Descripción')).replace('\n', ' ').strip()
            # Incluimos el índice local del chunk para que la IA sepa el orden
            texto_lote += f"ITEM_{idx}: {desc}\n"
        
        prompt = f"""
        Actúa como un Auditor Fiscal Senior. Tu tarea es clasificar masivamente un listado de movimientos bancarios.

        LAS CATEGORÍAS SON:
        1. VENTA (Ingresos por ventas, cobros a clientes, cupones, transferencias recibidas comerciales).
        2. NO_COMPUTABLE (Plazos fijos, préstamos, movimientos entre cuentas propias, devoluciones, errores operativos, gastos bancarios, impuestos).
        3. DUDA (Si la descripción es ambigua o vacía).

        INPUT DE DATOS (Formato: ITEM_ID: DESCRIPCIÓN):
        -----------------------------------------------
        {texto_lote}
        -----------------------------------------------

        INSTRUCCIONES DE SALIDA (CRÍTICO):
        - Debes devolver una respuesta para CADA uno de los items listados arriba.
        - El formato debe ser ESTRICTAMENTE una lista línea por línea: ID | CATEGORIA | SUSTENTO CORTO
        - NO escribas introducciones, ni conclusiones, ni markdown (```). Solo los datos.
        
        Ejemplo de Salida Esperada:
        ITEM_45: VENTA | Cobro de cliente identificado
        ITEM_46: NO_COMPUTABLE | Constitución de Plazo Fijo
        """
        return prompt

    def procesar_lote_con_retry(self, df_chunk, intento_actual=1):
        """
        Envía un lote a la API con lógica de reintento para errores 429.
        """
        prompt = self.generar_prompt_lote(df_chunk)
        max_intentos = 3

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            if not response.text:
                return {} # Retorna dict vacío si falla

            # Parseamos la respuesta de texto a un diccionario {Indice: (Categoria, Sustento)}
            resultados_lote = {}
            lineas = response.text.strip().split('\n')
            
            for linea in lineas:
                # Buscamos el patrón "ITEM_123: Categoria | Sustento"
                if "ITEM_" in linea and "|" in linea:
                    try:
                        parte_id, contenido = linea.split(':', 1)
                        idx = int(parte_id.replace("ITEM_", "").strip())
                        
                        if '|' in contenido:
                            cat, sus = contenido.split('|', 1)
                            resultados_lote[idx] = (cat.strip(), sus.strip())
                    except Exception:
                        continue # Si una línea falla, la saltamos (quedará como vacía)

            return resultados_lote

        except Exception as e:
            error_msg = str(e)
            if ("429" in error_msg or "Resource exhausted" in error_msg) and intento_actual <= max_intentos:
                wait_time = 20 * intento_actual # 20s, 40s, 60s
                logging.warning(f"⚠️ Cuota excedida (Lote). Esperando {wait_time}s para reintentar...")
                time.sleep(wait_time)
                return self.procesar_lote_con_retry(df_chunk, intento_actual + 1)
            else:
                logging.error(f"❌ Error irrecuperable en lote: {e}")
                return {}

    def clasificar_dataframe(self, df, columna_descripcion):
        logging.info(f"--- Iniciando Clasificación por LOTES (Batching) ---")
        
        # Inicializar columnas si no existen
        if 'Categoria_IA' not in df.columns: df['Categoria_IA'] = ''
        if 'Sustento_IA' not in df.columns: df['Sustento_IA'] = ''
        
        # Configuración del Chunking
        # 20 filas es un equilibrio seguro entre tokens y riesgo de desalineación
        CHUNK_SIZE = 20 
        total_filas = len(df)
        
        # Iterar por trozos
        for i in range(0, total_filas, CHUNK_SIZE):
            # Selección del chunk
            fin = min(i + CHUNK_SIZE, total_filas)
            df_chunk = df.iloc[i:fin]
            
            logging.info(f"Procesando lote {i//CHUNK_SIZE + 1} (Filas {i} a {fin})...")
            
            # Llamada a la IA
            resultados = self.procesar_lote_con_retry(df_chunk)
            
            # Asignación de resultados al DataFrame original
            # Usamos el índice original del DF para asegurar que el dato va a la fila correcta
            for idx, (categoria, sustento) in resultados.items():
                if idx in df.index:
                    df.at[idx, 'Categoria_IA'] = categoria
                    df.at[idx, 'Sustento_IA'] = sustento
                
            # Pequeña pausa de cortesía para enfriar la API (Rate Limiting preventivo)
            time.sleep(2)

        return df