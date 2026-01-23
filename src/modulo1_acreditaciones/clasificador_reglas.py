import pandas as pd

class ClasificadorReglas:
    def clasificar(self, df):
        """
        Clasifica movimientos basándose en palabras clave.
        Es instantáneo y no requiere Internet ni API Keys.
        """
        # Creamos las columnas si no existen
        if 'Categoria_IA' not in df.columns: df['Categoria_IA'] = ''
        if 'Sustento_IA' not in df.columns: df['Sustento_IA'] = ''

        # Aplicamos la lógica fila por fila
        for index, row in df.iterrows():
            desc = str(row['DESCRIPCION_FINAL']).upper()
            debito = row['Debito']
            credito = row['Credito']
            
            cat = "DUDA"
            sus = "Revisar manualmente"

            # --- 1. REGLAS DE GASTOS E IMPUESTOS (NO COMPUTABLE) ---
            if any(palabra in desc for palabra in ['IMPUESTO', 'LEY 25.413', 'I.V.A.', 'IIBB', 'SIRCREB', 'AFIP', 'AGIP', 'ARBA', 'RETENCION', 'PERCEPCION', 'VEP']):
                cat = "NO_COMPUTABLE"
                sus = "Impuestos y Retenciones"
            
            elif any(palabra in desc for palabra in ['COMISION', 'MANTENIMIENTO', 'GASTOS', 'IVA SOBRE', 'DB.ALIC.', 'SERVICIO', 'PAQUETE', 'TAS', 'ATM']):
                cat = "NO_COMPUTABLE"
                sus = "Gastos Bancarios"

            elif any(palabra in desc for palabra in ['CHEQUE', 'ECHEQ', 'CHQ', 'PAGO PROVEEDOR', 'DEBITO DIRECTO']):
                cat = "NO_COMPUTABLE"
                sus = "Pagos Operativos / Proveedores"
            
            elif any(palabra in desc for palabra in ['SUELDO', 'HABERES', 'NOMINA']):
                cat = "NO_COMPUTABLE"
                sus = "Sueldos y Cargas Sociales"

            # --- 2. REGLAS FINANCIERAS (NO COMPUTABLE) ---
            elif any(palabra in desc for palabra in ['PLAZO FIJO', 'FONDO COMUN', 'SUSCRIPCION', 'RESCATE', 'INVERSION']):
                cat = "NO_COMPUTABLE"
                sus = "Movimiento de Inversiones (Propio)"

            elif 'TRANSFERENCIA ENVIADA' in desc:
                cat = "NO_COMPUTABLE"
                sus = "Transferencia Saliente"

            # --- 3. REGLAS DE VENTAS (VENTA) ---
            # Si entra dinero (Crédito > 0) y no fue clasificado como "Rescate de fondo" ni nada anterior
            elif credito > 0:
                if any(palabra in desc for palabra in ['DEBIN', 'CREDITO INMEDIATO', 'TRANSFERENCIA RECIBIDA', 'ACREDITAMIENTO', 'VENTAS', 'CUPON', 'TARJETA']):
                    cat = "VENTA"
                    sus = "Cobro de Clientes / Ventas"
                elif cat == "DUDA": # Si aún no sabemos qué es, pero entró plata
                    cat = "VENTA"
                    sus = "Ingreso de Fondos (Presunta Venta)"

            # Guardamos en el DataFrame
            df.at[index, 'Categoria_IA'] = cat
            df.at[index, 'Sustento_IA'] = sus
        
        return df