import os
import logging
import time
import pandas as pd
from google import genai
from dotenv import load_dotenv

load_dotenv()

class ClasificadorMovimientos:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR CRÍTICO: Falta GEMINI_API_KEY")
        
        try:
            self.client = genai.Client(api_key=api_key)
            # Mantenemos el 2.0 que es el que tiene más cuota diaria
            self.model_name = "gemini-1.5-flash" 
        except Exception as e:
            logging.error(f"Error cliente IA: {e}")
            raise

    def generar_prompt_lote(self, df_chunk):
        texto_lote = ""
        for idx, fila in df_chunk.iterrows():
            desc = str(fila.get('DESCRIPCION_FINAL', '')).replace('\n', ' ').strip()
            monto_deb = fila.get('Debito', 0)
            monto_cred = fila.get('Credito', 0)
            texto_lote += f"ID_{idx}: {desc} (In: {monto_cred} / Out: {monto_deb})\n"
        
        return f"""
        Actúa como Auditor Fiscal. Clasifica estos movimientos.
        CATEGORÍAS: VENTA, NO_COMPUTABLE, DUDA.
        
        DATOS:
        {texto_lote}

        RESPONDER SOLO EN ESTE FORMATO (Una línea por ID):
        ID_xx: CATEGORIA | SUSTENTO CORTO
        """

    def procesar_lote(self, df_chunk):
        prompt = self.generar_prompt_lote(df_chunk)
        intentos = 0
        
        while intentos < 5: # Aumentamos intentos
            try:
                response = self.client.models.generate_content(
                    model=self.model_name, contents=prompt
                )
                
                if not response.text: return {}

                resultados = {}
                for linea in response.text.split('\n'):
                    if "ID_" in linea and "|" in linea:
                        try:
                            parte_id, contenido = linea.split(':', 1)
                            idx = int(parte_id.replace("ID_", "").strip())
                            cat, sus = contenido.split('|', 1)
                            resultados[idx] = (cat.strip(), sus.strip())
                        except: continue
                return resultados

            except Exception as e:
                # Si falla, esperamos UN MINUTO ENTERO antes de reintentar
                # Esto le da tiempo a tu cuenta de "enfriarse"
                logging.warning(f"⚠️ Google dice STOP (429). Esperando 60 segundos...")
                time.sleep(60) 
                intentos += 1
        
        return {}

    def clasificar_dataframe(self, df, columna_descripcion):
        logging.info(f"--- Iniciando Batching (MODO TORTUGA: 5 filas / 30 seg) ---")
        
        if 'Categoria_IA' not in df.columns: df['Categoria_IA'] = ''
        if 'Sustento_IA' not in df.columns: df['Sustento_IA'] = ''
        
        # === CONFIGURACIÓN ULTRA CONSERVADORA ===
        CHUNK_SIZE = 5      # Procesamos de a poquitos
        ESPERA_ENTRE_LOTES = 30 # Esperamos medio minuto entre llamadas
        # ========================================
        
        total = len(df)
        
        for i in range(0, total, CHUNK_SIZE):
            fin = min(i + CHUNK_SIZE, total)
            df_chunk = df.iloc[i:fin]
            
            logging.info(f"Procesando lote {i//CHUNK_SIZE + 1} (Filas {i} a {fin})...")
            
            resultados = self.procesar_lote(df_chunk)
            
            for idx, (cat, sus) in resultados.items():
                if idx in df.index:
                    df.at[idx, 'Categoria_IA'] = cat
                    df.at[idx, 'Sustento_IA'] = sus
            
            logging.info(f"⏳ Descansando {ESPERA_ENTRE_LOTES} segundos...")
            time.sleep(ESPERA_ENTRE_LOTES)

        return df