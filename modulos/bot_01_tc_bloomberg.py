import logging
from utilidades.excepciones import BusinessException
import variables_globales as vg
import subprocess
import json
import requests
from bs4 import BeautifulSoup
from lxml import html
from utilidades.httpclient import get_http_client
import re

logger = logging.getLogger("Bot 01 - Tipo cambio bloomberg")


def extrer_tipo_cambio_bloomberg(cfg):
    """
    Función para extraer el tipo de cambio de Bloomberg utilizando XPath y BeautifulSoup como fallback.
    Utiliza el httpclient de utilidades para realizar la petición HTTP.
    """
    tipo_cambio = None
    try:
        url = cfg["fuentes_tc"]["url_bloomberg"]
        
        i

        # Construir el comando curl con el proxy
        curl_cmd = [
            'curl',
            '--proxy',
            'http://a3da2aa31a50a4775a4758b9a880c924-1dc7a13991739a83.elb.us-east-1.amazonaws.com:3128',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            '-H', 'Accept-Language: en-US,en;q=0.9,es;q=0.8',
            url
        ]

        logger.info(f"Ejecutando comando curl: {' '.join(curl_cmd)}")

        # Ejecutar curl y capturar la salida
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    content = stdout.decode('utf-8')
                    break
                else:
                    logger.warning(f"Intento {retry_count + 1} falló, error: {stderr.decode()}")
                    retry_count += 1
            except Exception as e:
                logger.warning(f"Error en intento {retry_count + 1}: {str(e)}")
                retry_count += 1

        if retry_count == max_retries:
            logger.error("No se pudo obtener respuesta de Bloomberg después de todos los intentos")
            raise BusinessException("No se pudo conectar con Bloomberg")

        # Verificar que el contenido no esté corrupto o vacío
        if len(content) < 100:
            logger.error(f"El contenido de la respuesta es demasiado corto: {len(content)} caracteres")
            raise BusinessException("Contenido insuficiente recibido de Bloomberg")

        # Verificar que el contenido tenga caracteres válidos
        if not content.strip():
            logger.error("El contenido de la respuesta está vacío después de limpiar espacios")
            raise BusinessException("Contenido vacío recibido de Bloomberg")

        # Verificar que el contenido parezca HTML válido
        if not ('<' in content and '>' in content):
            logger.error("El contenido no parece ser HTML válido")
            raise BusinessException("Contenido no válido recibido de Bloomberg")

        # Método 1: Usando XPath con lxml
        try:
            tree = html.fromstring(content)
            xpath_selectors = [
                "//main//*[@data-component='sized-price']",
            ]
            for selector in xpath_selectors:
                elementos = tree.xpath(selector)
                if elementos:
                    for elemento in elementos:
                        texto = elemento.text_content().strip()
                        tipo_cambio = texto
                        logger.info(f"Tipo de cambio obtenido con XPath ({selector}): {tipo_cambio}")
                        return tipo_cambio
        except Exception as xpath_error:
            logger.warning(f"Error al usar XPath: {xpath_error}")
            
    except BusinessException as be:
        logger.error(f"Error de negocio: {be}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado al extraer el tipo de cambio de Bloomberg: {e}")
        raise BusinessException(f"Error inesperado al extraer el tipo de cambio: {str(e)}")
    finally:
        return tipo_cambio

def extraer_tipo_cambio_xe(cfg):
    """
    Función para extraer el tipo de cambio de xe.com utilizando XPath y BeautifulSoup como fallback.
    Utiliza el httpclient de utilidades para realizar la petición HTTP.
    """
    tipo_cambio = None
    http_client = get_http_client()
    
    try:
        url = cfg["fuentes_tc"]["url_xe_com"]
        response = http_client.make_request(url)
        if response is None:
            logger.error("No se pudo obtener respuesta de xe.com usando http_client")
            raise BusinessException("No se pudo conectar con xe.com (http_client)")
        
        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code} al acceder a xe.com")
            raise BusinessException(f"Error HTTP {response.status_code} al acceder a xe.com")
        
        soup = BeautifulSoup(response.text, "html.parser")
        conversion_div = soup.find('div', {'data-testid': 'conversion'})

        # Dentro de ese div, el segundo <p> contiene el valor, lo separamos del texto extra
        if conversion_div:
            p_tags = conversion_div.find_all('p')
            if len(p_tags) >= 2:
                raw_text = p_tags[1].text
                # Limpiar: Extraemos solo el número antes de "Peruvian Soles"
                tipo_cambio = raw_text.split('Peruvian')[0].strip()
                print(f"Tipo de cambio USD a PEN: {tipo_cambio}")
            else:
                print("No se encontró el segundo <p> esperado.")
        else:
            print("No se encontró el valor, probablemente requiere JavaScript.")
            
    except BusinessException as be:
        logger.error(f"Error de negocio: {be}")
    except Exception as e:
        logger.error(f"Error inesperado al extraer el tipo de cambio de xe.com: {e}")
    finally:
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
        #tipo_cambio_str = extraer_tipo_cambio_xe(cfg)
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