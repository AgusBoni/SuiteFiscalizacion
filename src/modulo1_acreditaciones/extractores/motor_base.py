import re
from decimal import Decimal, InvalidOperation

def limpiar_moneda(valor):
    """
    Convierte strings bancarios argentinos ($ 1.500,20) a Decimal(1500.20).
    Ignora basura, símbolos y espacios.
    """
    if not valor:
        return Decimal("0.00")
    
    # Convertimos a string y limpiamos espacios
    s = str(valor).strip()
    
    # Regex: Dejamos solo números, comas, puntos y signo menos
    # Esto elimina '$', letras, y espacios invisibles
    s_limpio = re.sub(r'[^\d.,-]', '', s)
    
    if not s_limpio:
        return Decimal("0.00")

    try:
        # LÓGICA ARGENTINA:
        # Caso 1: Tiene punto y coma (1.234,56) -> Punto es mil, Coma es decimal
        if '.' in s_limpio and ',' in s_limpio:
            s_limpio = s_limpio.replace('.', '') # Chao miles
            s_limpio = s_limpio.replace(',', '.') # Coma a punto Python
            
        # Caso 2: Solo tiene coma (1234,56) -> Es decimal
        elif ',' in s_limpio:
            s_limpio = s_limpio.replace(',', '.')
            
        # Caso 3: Solo tiene puntos (1.234.567) -> Son miles
        elif s_limpio.count('.') > 1:
            s_limpio = s_limpio.replace('.', '')
            
        return Decimal(s_limpio)
        
    except (InvalidOperation, ValueError):
        return Decimal("0.00")