import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

# Configuración básica de logs (para rastrear qué hace el programa)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProcesadorBancario:
    """
    Clase encargada de procesar los extractos bancarios.
    Objetivo: Convertir datos crudos en información auditable con ERROR 0.
    """

    def __init__(self, ruta_archivo):
        """
        Constructor de la clase.
        :param ruta_archivo: Ubicación del archivo Excel/CSV del banco.
        """
        self.ruta_archivo = ruta_archivo
        self.datos = None # Aquí guardaremos la tabla de datos
        self.total_control_pdf = Decimal('0.00') # Suma total que dice el PDF (input manual o extraído)

    def cargar_datos(self):
        """
        Carga el archivo en un DataFrame de Pandas.
        """
        try:
            # Leemos el excel. 'dtype=str' es vital para no perder ceros a la izquierda en CUITs
            self.datos = pd.read_excel(self.ruta_archivo, dtype=str)
            logging.info(f"Archivo cargado exitosamente: {self.ruta_archivo}")
            logging.info(f"Columnas detectadas: {self.datos.columns.tolist()}")
        except FileNotFoundError:
            logging.error(f"Error: No se encontró el archivo en {self.ruta_archivo}")
        except Exception as e:
            logging.error(f"Error inesperado al cargar datos: {e}")

    def limpiar_moneda(self, valor_texto):
        """
        Convierte texto '$ 1.500,00' a objeto Decimal('1500.00').
        Esta función es el corazón de la precisión financiera.
        """
        if pd.isna(valor_texto):
            return Decimal('0.00')
        
        # Eliminamos símbolos de moneda y espacios
        limpio = str(valor_texto).replace('$', '').replace(' ', '')
        
        # En Argentina/Latam: punto es mil, coma es decimal.
        # En Python/US: coma es mil, punto es decimal.
        # Reemplazamos punto por nada (eliminar separador miles) y coma por punto (decimal standard)
        limpio = limpio.replace('.', '').replace(',', '.')
        
        try:
            return Decimal(limpio)
        except InvalidOperation:
            logging.warning(f"No se pudo convertir el valor: {valor_texto}")
            return Decimal('0.00')

    def ejecutar_suma_control(self, columna_monto, total_esperado_pdf):
        """
        Suma de Control: Compara la suma de los datos cargados contra el total del PDF.
        :param columna_monto: Nombre de la columna que tiene los importes.
        :param total_esperado_pdf: El total que figura al final del extracto (verificación humana).
        """
        if self.datos is None:
            logging.error("No hay datos cargados para verificar.")
            return False

        # Aplicamos la limpieza a toda la columna de montos
        # apply() ejecuta la funcion limpiar_moneda fila por fila
        serie_convertida = self.datos[columna_monto].apply(self.limpiar_moneda)
        
        # Sumamos
        suma_calculada = serie_convertida.sum()
        total_esperado = Decimal(str(total_esperado_pdf)) # Aseguramos que sea Decimal

        diferencia = suma_calculada - total_esperado

        logging.info(f"--- REPORTE DE INTEGRIDAD ---")
        logging.info(f"Suma Calculada por Python: {suma_calculada}")
        logging.info(f"Total Esperado (PDF):      {total_esperado}")
        logging.info(f"Diferencia:                {diferencia}")

        if diferencia == Decimal('0.00'):
            logging.info("ESTADO: VALIDADO (ERROR 0). Se puede proceder.")
            return True
        else:
            logging.critical("ESTADO: FALLIDO. Los datos extraídos no coinciden con el PDF.")
            return False

# --- Bloque de prueba (solo se ejecuta si corres este archivo directamente) ---
if __name__ == "__main__":
    # Simulación de uso
    # Asumimos que tienes un excel en data/input/extracto_ejemplo.xlsx
    # Y que en el PDF el total dice 15000.50
    
    # NOTA: Esto fallará si no creas el archivo, es solo para mostrar la lógica de invocación.
    procesador = ProcesadorBancario("data/input/extracto_ejemplo.xlsx")
    # procesador.cargar_datos() 
    # procesador.ejecutar_suma_control("Monto", "15000.50")