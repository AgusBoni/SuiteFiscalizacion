import re
from decimal import Decimal, InvalidOperation

def limpiar_moneda(valor):
    """
    Convierte strings de moneda argentina ($ 1.500,20) a Decimal(1500.20).
    Soporta negativos y formatos sucios.
    """
    if not valor:
        return Decimal("0.00")
    
    # 1. Convertimos a string y quitamos espacios extra
    s = str(valor).strip()
    
    # 2. Quitamos todo lo que NO sea número, coma, punto o signo menos
    #    Ej: "$ 173.491.540,11"  -> "173.491.540,11"
    #    Ej: "USD 100" -> "100"
    s_limpio = re.sub(r'[^\d.,-]', '', s)
    
    if not s_limpio:
        return Decimal("0.00")

    try:
        # 3. Lógica de detección de formato Argentina/España (1.000,00)
        # Si tiene puntos y comas, asumimos que el punto es miles y la coma decimal.
        if '.' in s_limpio and ',' in s_limpio:
            s_limpio = s_limpio.replace('.', '') # Borramos los miles (173491540,11)
            s_limpio = s_limpio.replace(',', '.') # Cambiamos coma por punto decimal (173491540.11)
        
        # Si solo tiene coma (120,50), es decimal seguro en formato AR
        elif ',' in s_limpio:
            s_limpio = s_limpio.replace(',', '.')
            
        # Si tiene múltiples puntos (1.200.500), son miles seguro.
        elif s_limpio.count('.') > 1:
            s_limpio = s_limpio.replace('.', '')

        return Decimal(s_limpio)
        
    except (InvalidOperation, ValueError):
        # Si falla algo extremo, devolvemos 0 para no romper el programa
        return Decimal("0.00")