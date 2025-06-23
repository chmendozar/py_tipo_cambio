import logging
import configparser
import requests
from utilidades.excepciones import BusinessException
import variables_globales as vg

logger = logging.getLogger("Bot 04 - Registrar TC")

def bot_run(cfg, mensaje="Bot 04 - Registrar TC"):
    resultado = False
    try:
        # Leer configuración
        config = configparser.ConfigParser()
        config.read(cfg)
        username = "dcelis"
        password = "U2FsdGVkX198pE6U0Hw/wJgC7vKhQwXbOmPUrylyeZI="
        # Leer URLs desde el archivo de configuración
       
        login_url = f"{cfg['api'] ['api_modulo_login']}"        
        exchange_rate_save_url = f"{cfg['api'] ['api_modulo_tc_add']}"
        exchange_rate_get_url = f"{cfg['api'] ['api_modulo_tc_get']}"

        # Crear una sesión para mantener las cookies
        session = requests.Session()

        # Datos del formulario de inicio de sesión
        login_data = {
            "username": username, 
            "password": password 
        }

        # Encabezados de la solicitud
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Realizar la solicitud POST para iniciar sesión
        login_response = session.post(login_url, data=login_data, headers=headers)

        # Verificar si el inicio de sesión fue exitoso
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get("data") == "valid":
                logger.info(f"Inicio de sesión exitoso. Bienvenido {login_result.get('username')}!")

                exchange_rate_data = {
                "user": username,
                "exchangeRate":vg.tipo_cambio_bloomberg                
                }
                # Realizar la solicitud POST para guardar el tipo de cambio
                exchange_rate_response = session.post(exchange_rate_save_url, data=exchange_rate_data, headers=headers)

                # Verificar si la solicitud fue exitosa
                if exchange_rate_response.status_code == 200:
                    response_json = exchange_rate_response.json()
                    logger.info("Respuesta del servidor: %s", response_json)
                    
                    
                else:
                    logger.error(f"Error al guardar el tipo de cambio: {exchange_rate_response.status_code}")
                exchange_rate_get_url = session.get(exchange_rate_get_url, headers=headers)
                    
                if  exchange_rate_get_url.status_code == 200:
                    response_json = exchange_rate_get_url.json()
                    logger.info("Respuesta del servidor: %s", response_json)
                    primer_item = response_json['dataExchage'][0]
                    vg.tipo_cambio_venta = primer_item['tc_venta']
                    vg.tipo_cambio_compra = primer_item['tc_compra']
                    resultado = True

            else:
                raise BusinessException(f"Inicio de sesión fallido. Mensaje: {login_result.get('mensaje')}")
        else:
            raise BusinessException(f"Error en la solicitud de inicio de sesión: {login_response.status_code}")

    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
    except Exception as e:
        logger.error(f"Error inesperado en bot_run: {e}")
        mensaje = f"Error inesperado: {e}"
    finally:
        logger.info("Fin del bot: %s", mensaje)
        return resultado, mensaje