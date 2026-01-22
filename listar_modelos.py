import os
from google import genai
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- INICIANDO DIAGNÓSTICO DE CONEXIÓN ---")

if not api_key:
    print("ERROR: No se leyó la API KEY del archivo .env")
else:
    print("Clave detectada. Consultando a Google...")
    try:
        # Iniciamos cliente
        client = genai.Client(api_key=api_key)
        
        # Pedimos la lista simple
        pager = client.models.list()
        
        print("\nMODELOS DISPONIBLES PARA TI:")
        print("---------------------------")
        count = 0
        for model in pager:
            # Solo imprimimos el nombre para evitar errores
            print(f" -> {model.name}")
            count += 1
            
        if count == 0:
            print("ALERTA: Google respondió, pero la lista está vacía.")
            print("Posible causa: La API 'Generative Language API' no está habilitada en tu cuenta de Google Cloud.")
            
    except Exception as e:
        print(f"\nERROR CRÍTICO: {e}")
        print("\nConsejo: Si el error es 404 aquí también, tu API Key podría no ser válida o el servicio está caído.")