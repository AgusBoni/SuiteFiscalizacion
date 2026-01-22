import os
import logging
from google import genai # <--- NUEVA LIBRERÍA
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ClasificadorMovimientos:
    def __init__(self):
        # 1. Obtenemos la clave del entorno
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR CRÍTICO: No se encontró la GEMINI_API_KEY en el archivo .env")
        
        # 2. Configuración NUEVA (Cliente directo)
        try:
            self.client = genai.Client(api_key=api_key)
            # Usamos el modelo Flash que es rápido y económico
            self.model_name = "gemini-2.0-flash" 
        except Exception as e:
            logging.error(f"Error configurando cliente Gemini: {e}")
            raise

    def consultar_inteligencia_artificial(self, descripcion):
        """
        Consulta a la IA usando la nueva librería google-genai.
        """
        prompt = f"""
        Actúa como auditor fiscal experto. Clasifica este movimiento bancario: "{descripcion}"
        
        Responde ESTRICTAMENTE con este formato: CATEGORIA | SUSTENTO
        
        Las categorías posibles son:
        - VENTA (Cobros, cupones, depósitos de terceros, transferencias recibidas de clientes)
        - NO_COMPUTABLE (Préstamos, plazos fijos, transferencias propias, reversiones, errores operativos)
        - DUDA (Si no es claro)

        Ejemplo 1: "Transf. de Juana Perez" -> VENTA | Es un cobro de cliente.
        Ejemplo 2: "Const. Plazo Fijo" -> NO_COMPUTABLE | Es inversión, no venta.
        """
        
        try:
            # 3. Llamada NUEVA
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Verificamos si hay respuesta
            if response.text:
                return response.text.strip()
            else:
                return "DUDA | La IA no devolvió texto."
                
        except Exception as e:
            # Capturamos el error sin romper el programa, pero lo mostramos
            logging.warning(f"Fallo IA para '{descripcion}': {e}")
            return "ERROR_API | Fallo de conexión"

    def clasificar_dataframe(self, df, columna_descripcion):
        logging.info(f"--- Iniciando clasificación con IA ({self.model_name}) ---")
        
        # Creamos columnas vacías si no existen
        if 'Categoria_IA' not in df.columns:
            df['Categoria_IA'] = ''
        if 'Sustento_IA' not in df.columns:
            df['Sustento_IA'] = ''

        # Contador para mostrar progreso
        total = len(df)
        
        for index, fila in df.iterrows():
            descripcion = fila[columna_descripcion]
            
            # Logs de progreso cada 10 filas para no saturar la pantalla
            if index % 10 == 0:
                logging.info(f"Procesando fila {index + 1} de {total}...")

            resultado_completo = self.consultar_inteligencia_artificial(descripcion)
            
            # Parsing (Separar Categoría | Sustento)
            try:
                if '|' in resultado_completo:
                    categoria, sustento = resultado_completo.split('|', 1)
                    df.at[index, 'Categoria_IA'] = categoria.strip()
                    df.at[index, 'Sustento_IA'] = sustento.strip()
                else:
                    df.at[index, 'Categoria_IA'] = 'DUDA'
                    df.at[index, 'Sustento_IA'] = resultado_completo
            except Exception:
                df.at[index, 'Categoria_IA'] = 'ERROR'
                df.at[index, 'Sustento_IA'] = 'Error procesando respuesta'

        return df