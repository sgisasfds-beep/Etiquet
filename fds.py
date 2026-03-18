import os
import re
import fitz  # PyMuPDF
import pandas as pd
import logging
from pathlib import Path
import pytesseract
from PIL import Image
import io

# Configuración de log para ver el progreso real
logging.basicConfig(level=logging.INFO, format='%(message)s')

# ==============================================================================
# CONFIGURACIÓN CRÍTICA: RUTA DE TESSERACT
# Verifica que esta ruta coincida con donde instalaste Tesseract en tu Windows.
# ==============================================================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Expresión regular blindada contra errores tipográficos del OCR (ej: o por 0)
PATRON_BUSQUEDA = re.compile(
    r"(palabra\s*de\s*advertencia|palabra\s*de\s*se[ñn]al|palabra\s*de\s*peligro|signal\s*word)"
    r"[\s\:\.\-\n]*"
    r"(peligr[o0]|atenci[oó0][nñ]|advertencia|danger|warning|ninguna|none)",
    re.IGNORECASE
)

def normalizar_resultado(palabra_cruda):
    """
    Limpia los errores de lectura del OCR para que el Excel quede inmaculado.
    """
    p = palabra_cruda.lower()
    if "peligr" in p or "danger" in p: return "Peligro"
    if "atenci" in p or "warning" in p: return "Atención"
    if "advertencia" in p: return "Advertencia"
    if "ningun" in p or "none" in p: return "Ninguna"
    return palabra_cruda.capitalize()

def procesar_pdf_con_doble_capa(pdf_path):
    """
    Intenta extraer texto nativo. Si falla o no encuentra la palabra,
    transforma el PDF en imágenes de alta resolución y aplica OCR.
    """
    texto_nativo = ""
    paginas_cargadas = []

    try:
        with fitz.open(pdf_path) as doc:
            # Limitar a las primeras 4 páginas (Sección 2 GHS/SGA) para máxima velocidad
            max_pages = min(4, len(doc))

            # ---------------------------------------------------------
            # CAPA 1: EXTRACCIÓN NATIVA (Rápida)
            # ---------------------------------------------------------
            for page_num in range(max_pages):
                pagina = doc.load_page(page_num)
                paginas_cargadas.append(pagina)
                texto_nativo += pagina.get_text("text") + "\n"

            coincidencia = PATRON_BUSQUEDA.search(texto_nativo)
            if coincidencia:
                return normalizar_resultado(coincidencia.group(2))

            # ---------------------------------------------------------
            # CAPA 2: EXTRACCIÓN OCR (Fuerza Bruta para Escaneados)
            # ---------------------------------------------------------
            # Si llegamos aquí, es un PDF escaneado o el texto tiene formato extraño
            texto_ocr = ""
            for pagina in paginas_cargadas:
                # Matriz 3x3 aumenta la resolución a ~200 DPI (ideal para OCR)
                pix = pagina.get_pixmap(matrix=fitz.Matrix(3, 3))
                img = Image.open(io.BytesIO(pix.tobytes("png")))

                # Ejecutamos Tesseract en español e inglés
                texto_ocr += pytesseract.image_to_string(img, lang='spa+eng') + "\n"

            coincidencia_ocr = PATRON_BUSQUEDA.search(texto_ocr)
            if coincidencia_ocr:
                return normalizar_resultado(coincidencia_ocr.group(2)) + " (Vía OCR)"

            return "No encontrada / Revisión manual requerida"

    except pytesseract.pytesseract.TesseractNotFoundError:
        return "ERROR FATAL: Tesseract no está instalado o la ruta es incorrecta"
    except fitz.FileDataError:
        return "Error: Archivo corrupto"
    except fitz.FileEncryptedError:
        return "Error: PDF protegido con contraseña"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

def generar_reporte(ruta_carpeta, ruta_salida_excel):
    carpeta = Path(ruta_carpeta)

    if not carpeta.exists() or not carpeta.is_dir():
        logging.error(f"La ruta {ruta_carpeta} no existe.")
        return

    archivos_pdf = list(carpeta.glob("*.pdf"))
    total_archivos = len(archivos_pdf)

    if total_archivos == 0:
        logging.warning("No hay archivos PDF en la carpeta.")
        return

    logging.info(f"Iniciando escaneo de {total_archivos} Fichas de Seguridad...")
    logging.info("Nota: Los PDFs escaneados tomarán unos segundos adicionales por el OCR.\n")

    resultados = []

    for i, archivo in enumerate(archivos_pdf, 1):
        nombre_archivo = archivo.name
        logging.info(f"[{i}/{total_archivos}] Procesando: {nombre_archivo}")

        resultado_palabra = procesar_pdf_con_doble_capa(str(archivo))

        resultados.append({
            "Nombre del Archivo": nombre_archivo,
            "Palabra de Advertencia": resultado_palabra
        })

    # Exportar a Excel a prueba de fallos
    df = pd.DataFrame(resultados)
    try:
        df.to_excel(ruta_salida_excel, index=False, engine='openpyxl')
        logging.info(f"\n¡ÉXITO! Excel generado en: {ruta_salida_excel}")
    except PermissionError:
        ruta_alternativa = ruta_salida_excel.replace(".xlsx", "_COPIA.xlsx")
        df.to_excel(ruta_alternativa, index=False, engine='openpyxl')
        logging.warning(f"\nEl Excel original estaba abierto. Se guardó como: {ruta_alternativa}")

# ==========================================
# PUNTO DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    RUTA_ORIGEN = r"C:\Users\1022966950\Documents\FICHAS DE SEGURIDAD"
    RUTA_DESTINO = r"C:\Users\1022966950\Documents\FICHAS DE SEGURIDAD\Reporte_Palabras_SGA.xlsx"

    generar_reporte(RUTA_ORIGEN, RUTA_DESTINO)
