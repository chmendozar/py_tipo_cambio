import logging
from utilidades.excepciones import BusinessException
import variables_globales as vg
import requests
from bs4 import BeautifulSoup
from lxml import html
from utilidades.httpclient import get_http_client
import re

logger = logging.getLogger("Bot 01 - Tipo cambio bloomberg")

def is_valid_exchange_rate(text):
    """
    Valida si el texto parece ser un tipo de cambio válido.
    """
    if not text or not isinstance(text, str):
        return False
    
    # Limpiar el texto de caracteres no deseados
    cleaned_text = re.sub(r'[^\d.]', '', text)
    
    # Verificar que tenga el formato correcto (número decimal con máximo 2 decimales)
    if not re.match(r'^\d+\.\d{1,2}$', cleaned_text):
        return False
    
    # Verificar que el valor esté en un rango razonable (entre 1 y 10)
    try:
        value = float(cleaned_text)
        return 1.0 <= value <= 10.0
    except ValueError:
        return False

def extrer_tipo_cambio_bloomberg(cfg):
    """
    Función para extraer el tipo de cambio de Bloomberg utilizando XPath y BeautifulSoup como fallback.
    Utiliza el httpclient de utilidades para realizar la petición HTTP.
    """
    tipo_cambio = None
    http_client = get_http_client()
    try:
        url = cfg["fuentes_tc"]["url_bloomberg"]
        # Usar un User-Agent menos común para evitar detección de actividad inusual
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",  # Asegurar que aceptamos compresión
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        response = http_client.make_request(url, headers=headers)
        if response is None:
            logger.error("No se pudo obtener respuesta de Bloomberg usando http_client")
            raise BusinessException("No se pudo conectar con Bloomberg (http_client)")

        # Verificar que la respuesta sea válida
        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code} al acceder a Bloomberg")
            raise BusinessException(f"Error HTTP {response.status_code} al acceder a Bloomberg")

        # Verificar el tipo de contenido
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type and 'application/json' not in content_type:
            logger.warning(f"Tipo de contenido inesperado: {content_type}")

        # Verificar si el contenido está comprimido
        content_encoding = response.headers.get('content-encoding', '').lower()
        logger.info(f"Content-Type: {content_type}")
        logger.info(f"Content-Encoding: {content_encoding}")
        logger.info(f"Content-Length: {len(response.content)} bytes")

        # Intentar decodificar el contenido correctamente
        try:
            # Si el contenido está comprimido, requests debería descomprimirlo automáticamente
            # pero vamos a verificar si hay problemas
            if content_encoding:
                logger.info(f"Contenido comprimido detectado: {content_encoding}")
                # Intentar acceder al contenido descomprimido
                if hasattr(response, 'text'):
                    content = response.text
                    logger.info("Usando response.text (descomprimido automáticamente)")
                else:
                    # Fallback: intentar decodificar manualmente
                    content = response.content.decode('utf-8')
                    logger.info("Usando response.content.decode() como fallback")
            else:
                # No está comprimido, usar response.text directamente
                content = response.text
                logger.info("Contenido no comprimido, usando response.text")
                
        except UnicodeDecodeError as e:
            logger.warning(f"Error decodificando con response.text: {e}")
            try:
                # Intentar decodificar como UTF-8 primero
                content = response.content.decode('utf-8')
                logger.info("Decodificación UTF-8 exitosa")
            except UnicodeDecodeError:
                try:
                    # Si falla UTF-8, intentar con latin-1
                    content = response.content.decode('latin-1')
                    logger.info("Decodificación latin-1 exitosa")
                except UnicodeDecodeError:
                    logger.error("No se pudo decodificar el contenido de la respuesta")
                    raise BusinessException("Error al decodificar el contenido de Bloomberg")

        # Verificar que el contenido no esté corrupto o vacío
        if len(content) < 100:
            logger.error(f"El contenido de la respuesta es demasiado corto: {len(content)} caracteres")
            logger.error(f"Primeros 200 caracteres: {repr(content[:200])}")
            raise BusinessException("Contenido insuficiente recibido de Bloomberg")

        # Verificar que el contenido tenga caracteres válidos
        if not content.strip():
            logger.error("El contenido de la respuesta está vacío después de limpiar espacios")
            raise BusinessException("Contenido vacío recibido de Bloomberg")

        # Verificar que el contenido parezca HTML válido
        if not ('<' in content and '>' in content):
            logger.error("El contenido no parece ser HTML válido")
            logger.error(f"Primeros 500 caracteres: {repr(content[:500])}")
            raise BusinessException("Contenido no válido recibido de Bloomberg")

        # Imprimir el contenido de la respuesta para depuración (solo los primeros 500 caracteres)
        logger.debug(f"Contenido de la respuesta: {content[:500]}...")

        # Método 1: Usando XPath con lxml de manera más flexible
        try:
            tree = html.fromstring(content)
            # Intentar varios selectores XPath más específicos para Bloomberg
            xpath_selectors = [
                "//div[contains(@class, 'priceText')]",
                "//span[contains(@class, 'priceText')]",
                "//div[contains(@class, 'value')]",
                "//span[contains(@class, 'value')]",
                "//div[contains(@class, 'price')]",
                "//span[contains(@class, 'price')]",
                "//*[contains(@class, 'price')]",
                "//div[contains(text(), '.') and contains(text(), 'USD')]",
                "//span[contains(text(), '.') and contains(text(), 'USD')]",
                "//div[contains(text(), '.')]",  # Buscar números con punto decimal
                "//span[contains(text(), '.')]"
            ]
            
            for selector in xpath_selectors:
                elementos = tree.xpath(selector)
                if elementos:
                    for elemento in elementos:
                        texto = elemento.text_content().strip()
                        if texto and '.' in texto and is_valid_exchange_rate(texto):
                            tipo_cambio = texto
                            logger.info(f"Tipo de cambio obtenido con XPath ({selector}): {tipo_cambio}")
                            return tipo_cambio
        except Exception as xpath_error:
            logger.warning(f"Error al usar XPath: {xpath_error}, intentando con BeautifulSoup...")
        
        # Método 2: BeautifulSoup con búsqueda más exhaustiva
        soup = BeautifulSoup(content, "html.parser")
        
        # Buscar cualquier elemento que pueda contener el precio
        posibles_elementos = soup.find_all(['div', 'span', 'p'], 
            class_=lambda x: x and ('price' in x.lower() or 'value' in x.lower()))
        
        for elemento in posibles_elementos:
            texto = elemento.text.strip()
            if texto and '.' in texto and is_valid_exchange_rate(texto):
                tipo_cambio = texto
                logger.info(f"Tipo de cambio obtenido con BeautifulSoup: {tipo_cambio}")
                return tipo_cambio
        
        # Si aún no encontramos nada, buscar cualquier texto que parezca un precio válido
        for elemento in soup.find_all(text=True):
            texto = elemento.strip()
            if texto and '.' in texto and is_valid_exchange_rate(texto):
                tipo_cambio = texto
                logger.info(f"Tipo de cambio obtenido por búsqueda de texto: {tipo_cambio}")
                return tipo_cambio
            
        # Si llegamos aquí, ningún método funcionó
        raise BusinessException("No se encontró el tipo de cambio en la página de Bloomberg con ningún método")
            
    except BusinessException as be:
        # Reenviar excepciones de negocio
        logger.error(f"Error de negocio: {be}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al extraer el tipo de cambio de Bloomberg: {e}")
        raise BusinessException(f"Error inesperado al extraer el tipo de cambio: {str(e)}")
    finally:
        # Si llegamos aquí sin encontrar el tipo de cambio, será None
        return tipo_cambio

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

def bot_run(cfg, mensaje="Bot 01 - Tipo cambio bloomberg"):
    resultado = False
    try:
        logger.info(f"Iniciando {mensaje}")
        tipo_cambio_str = extrer_tipo_cambio_bloomberg(cfg)
        
        if tipo_cambio_str:
            # Convertir a número si es necesario
            tipo_cambio_num = limpiar_tipo_cambio(tipo_cambio_str)
            logger.info(f"Tipo de cambio de Bloomberg extraído con éxito: {tipo_cambio_num}")
            vg.tipo_cambio_bloomberg = tipo_cambio_num
            resultado = True
        else:
            logger.warning("No se pudo obtener el tipo de cambio")
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