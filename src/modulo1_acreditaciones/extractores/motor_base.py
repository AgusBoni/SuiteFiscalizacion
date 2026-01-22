# src/modulo1_acreditaciones/extractores/motor_base.py
from decimal import Decimal, InvalidOperation
import logging

def limpiar_moneda(valor):
    """
    Convierte string '$ 1.500,00' -> Decimal('1500.00')
    Maneja el formato Argentina/Latam: 
    - Miles = Punto
    - Decimales = Coma
    """
    if not valor:
        return Decimal('0.00')
    
    # Convertimos a string por seguridad y limpiamos espacios
    v = str(valor).strip()
    
    # Quitamos símbolos de moneda y espacios internos
    v = v.replace('$', '').replace(' ', '')
    
    # En caso de negativos con paréntesis (ej: (500,00)) -> -500.00
    es_negativo = False
    if '(' in v and ')' in v:
        es_negativo = True
        v = v.replace('(', '').replace(')', '')
    elif '-' in v:
        # A veces el menos está al final "500-"
        es_negativo = True
        v = v.replace('-', '')

    # Reemplazo crítico: eliminar punto de miles, cambiar coma decimal por punto
    v = v.replace('.', '').replace(',', '.')
    
    try:
        numero = Decimal(v)
        return -numero if es_negativo else numero
    except InvalidOperation:
        return Decimal('0.00')