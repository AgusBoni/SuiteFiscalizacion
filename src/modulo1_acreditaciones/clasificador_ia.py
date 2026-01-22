import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables de entorno (busca el archivo .env)
load_dotenv()

class ClasificadorMovimientos:
    def __init__(self):
        # Configurar la API con la clave secreta
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("ERROR: No se encontró la GEMINI_API_KEY en el archivo .env")
        
        genai.configure(api_key=api_key)
        # Usamos el modelo gemini-pro (optimizado para texto)
        self.model = genai.GenerativeModel('gemini-pro')

    def consultar_inteligencia_artificial(self, descripcion):
        """
        Consulta real a Gemini. Pide Categoría y Sustento.
        """
        prompt = f"""
        Actúa como auditor fiscal experto en Argentina.
        Analiza este movimiento bancario: "{descripcion}"
        
        Tu tarea es clasificarlo y justificarlo brevemente.
        Responde ESTRICTAMENTE con este formato: CATEGORIA | SUSTENTO
        
        Las categorías posibles son:
        - VENTA (Cobros, cupones, depósitos de terceros)
        - NO_COMPUTABLE (Préstamos, plazos fijos, transferencias propias, reversiones)
        - DUDA (Si no es claro)

        Ejemplo de respuesta: NO_COMPUTABLE | Es una constitución de plazo fijo, no es ingreso gravado.
        """
        
        try:
            response = self.model.generate_content(prompt)
            texto_respuesta = response.text.strip() # Limpiamos espacios
            return texto_respuesta
        except Exception as e:
            logging.error(f"Fallo en API Gemini para '{descripcion}': {e}")
            return "ERROR_API | Fallo de conexión"

    def clasificar_dataframe(self, df, columna_descripcion):
        logging.info("--- Iniciando clasificación con IA (Esto puede demorar) ---")
        
        df['Categoria_IA'] = ''
        df['Sustento_IA'] = ''

        # Iteramos (en producción masiva usaríamos lotes/batching, pero para empezar iterrows está bien)
        for index, fila in df.iterrows():
            descripcion = fila[columna_descripcion]
            
            # Llamada a la IA
            resultado_completo = self.consultar_inteligencia_artificial(descripcion)
            
            # Separamos la respuesta usando el "pipe" (|)
            try:
                categoria, sustento = resultado_completo.split('|', 1)
                df.at[index, 'Categoria_IA'] = categoria.strip()
                df.at[index, 'Sustento_IA'] = sustento.strip()
            except ValueError:
                # Si la IA no respetó el formato
                df.at[index, 'Categoria_IA'] = 'DUDA'
                df.at[index, 'Sustento_IA'] = f'Formato inesperado: {resultado_completo}'

        return df