import logging
from utilidades.excepciones import BusinessException
import variables_globales as vg
import requests
from bs4 import BeautifulSoup
from lxml import html

logger = logging.getLogger("Bot 05 - Tipo cambio sbs")

def extraer_tipo_cambio_sbs(cfg):
    """
    Función para extraer el tipo de cambio de la SBS utilizando XPath y BeautifulSoup como fallback.
    Retorna una tupla con (tipo_cambio_venta, tipo_cambio_compra)
    """
    tipo_cambio_compra = None
    tipo_cambio_venta = None
    
    try:
        url = cfg["url"]["url_sbs"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Método 1: Usando XPath con lxml
        try:
            tree = html.fromstring(response.content)
            # XPath para encontrar la fila del Dólar de N.A.
            xpath_dolar_row = "//td[contains(text(), 'Dólar de N.A.')]/parent::tr"
            dolar_row = tree.xpath(xpath_dolar_row)
            
            if dolar_row and len(dolar_row) > 0:
                # XPath para el valor de compra (segunda columna de la fila)
                xpath_compra = ".//td[2]"
                # XPath para el valor de venta (tercera columna de la fila)
                xpath_venta = ".//td[3]"
                
                compra_element = dolar_row[0].xpath(xpath_compra)
                venta_element = dolar_row[0].xpath(xpath_venta)
                
                if compra_element and len(compra_element) > 0:
                    tipo_cambio_compra = compra_element[0].text_content().strip()
                    logger.info(f"Tipo de cambio compra obtenido con XPath: {tipo_cambio_compra}")
                
                if venta_element and len(venta_element) > 0:
                    tipo_cambio_venta = venta_element[0].text_content().strip()
                    logger.info(f"Tipo de cambio venta obtenido con XPath: {tipo_cambio_venta}")
                
                # Si se encontraron ambos valores, retornamos la tupla
                if tipo_cambio_compra and tipo_cambio_venta:
                    return tipo_cambio_venta, tipo_cambio_compra
        except Exception as xpath_error:
            logger.warning(f"Error al usar XPath: {xpath_error}, intentando con BeautifulSoup...")
        
        # Método 2: Usando BeautifulSoup como fallback
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Buscar la fila que contiene "Dólar de N.A."
        dolar_row = soup.find("td", string=lambda text: text and "Dólar de N.A." in text)
        
        if dolar_row and dolar_row.parent:
            # Obtener todas las celdas de la fila
            celdas = dolar_row.parent.find_all("td")
            
            if len(celdas) >= 3:
                if celdas[1].text.strip():
                    tipo_cambio_compra = celdas[1].text.strip()
                    logger.info(f"Tipo de cambio compra obtenido con BeautifulSoup: {tipo_cambio_compra}")
                
                if celdas[2].text.strip():
                    tipo_cambio_venta = celdas[2].text.strip()
                    logger.info(f"Tipo de cambio venta obtenido con BeautifulSoup: {tipo_cambio_venta}")
                
                # Retornamos la tupla si encontramos ambos valores
                if tipo_cambio_compra and tipo_cambio_venta:
                    return tipo_cambio_venta, tipo_cambio_compra
        
        # Método 3: Intentar buscar en la tabla por clase o estructura
        tabla = soup.find("table", class_="rgMasterTable")
        if tabla:
            filas = tabla.find_all("tr")
            for fila in filas:
                celdas = fila.find_all("td")
                if celdas and len(celdas) >= 3 and "Dólar de N.A." in celdas[0].text:
                    if celdas[1].text.strip():
                        tipo_cambio_compra = celdas[1].text.strip()
                    if celdas[2].text.strip():
                        tipo_cambio_venta = celdas[2].text.strip()
                    
                    # Retornamos la tupla si encontramos ambos valores
                    if tipo_cambio_compra and tipo_cambio_venta:
                        logger.info(f"Tipo de cambio compra/venta encontrado en tabla: {tipo_cambio_compra}/{tipo_cambio_venta}")
                        return tipo_cambio_venta, tipo_cambio_compra
            
        # Si llegamos aquí, ningún método funcionó
        raise BusinessException("No se encontró el tipo de cambio en la página de la SBS con ningún método")
            
    except requests.exceptions.RequestException as req_error:
        logger.error(f"Error en la solicitud HTTP: {req_error}")
        raise BusinessException(f"Error al conectar con la SBS: {str(req_error)}")
    except BusinessException as be:
        # Reenviar excepciones de negocio
        logger.error(f"Error de negocio: {be}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al extraer el tipo de cambio de la SBS: {e}")
        raise BusinessException(f"Error inesperado al extraer el tipo de cambio: {str(e)}")
    finally:
        # Si llegamos aquí sin encontrar el tipo de cambio completo, intentamos retornar lo que tengamos
        if tipo_cambio_venta and tipo_cambio_compra:
            return tipo_cambio_venta, tipo_cambio_compra
        elif tipo_cambio_venta:
            return tipo_cambio_venta, None
        elif tipo_cambio_compra:
            return None, tipo_cambio_compra
        return None, None

def limpiar_tipo_cambio(tipo_cambio_str):
    """
    Limpia el string del tipo de cambio para convertirlo a un número flotante.
    """
    if not tipo_cambio_str:
        return None
        
    try:
        # Elimina caracteres no numéricos excepto el punto decimal
        import re
        numero_limpio = re.sub(r'[^\d.]', '', tipo_cambio_str)
        return float(numero_limpio)
    except ValueError:
        logger.error(f"No se pudo convertir '{tipo_cambio_str}' a un número")
        return None

def bot_run(cfg, mensaje="Bot 01 - Tipo cambio sbs"):
    resultado = False
    try:
        logger.info(f"Iniciando {mensaje}")
        tipo_cambio_venta, tipo_cambio_compra = extraer_tipo_cambio_sbs(cfg)
        
        if tipo_cambio_venta and tipo_cambio_compra:
            # Convertir a números si es necesario
            tipo_cambio_venta_num = limpiar_tipo_cambio(tipo_cambio_venta)
            tipo_cambio_compra_num = limpiar_tipo_cambio(tipo_cambio_compra)
            
            logger.info(f"Tipo de cambio SBS extraído con éxito - Venta: {tipo_cambio_venta_num}, Compra: {tipo_cambio_compra_num}")
            vg.tipo_cambio_venta = tipo_cambio_venta_num
            vg.tipo_cambio_compra = tipo_cambio_compra_num
            resultado = True
        elif tipo_cambio_venta:
            tipo_cambio_venta_num = limpiar_tipo_cambio(tipo_cambio_venta)
            logger.info(f"Solo se pudo obtener el tipo de cambio de venta: {tipo_cambio_venta_num}")
            vg.tipo_cambio_sbs_venta = tipo_cambio_venta_num
            resultado = True
        elif tipo_cambio_compra:
            tipo_cambio_compra_num = limpiar_tipo_cambio(tipo_cambio_compra)
            logger.info(f"Solo se pudo obtener el tipo de cambio de compra: {tipo_cambio_compra_num}")
            vg.tipo_cambio_sbs_compra = tipo_cambio_compra_num
            resultado = True
        else:
            logger.warning("No se pudo obtener ningún tipo de cambio")
            resultado = False
        
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
        resultado = False
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
        resultado = False
    finally:
        logger.info("Fin del proceso ...")
        return resultado, mensaje