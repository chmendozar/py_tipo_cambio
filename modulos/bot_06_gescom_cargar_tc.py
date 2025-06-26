import logging
from utilidades.excepciones import BusinessException
import variables_globales as vg

logger = logging.getLogger("Bot 06 - Gescom Cargar TC")

def cargar_tc_gescom(cfg):
    try:
        logger.info("Iniciando carga de tipo de cambio en Gescom")
        
        import requests
        from datetime import datetime
        
        url = cfg["api"]["api_gescom_tc_sbs"]
        
        payload = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "venta": vg.tipo_cambio_venta,
            "compra": vg.tipo_cambio_compra
        }
        
        logger.info(f"Enviando request a Gescom con payload: {payload}")
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        if response.status_code == 200:
            resultado = True
            mensaje = "Carga de tipo de cambio en Gescom completada exitosamente"
            logger.info(f"Respuesta exitosa de Gescom: {response.text}")
        else:
            resultado = False
            mensaje = f"Error al cargar tipo de cambio en Gescom. Status: {response.status_code}"
            logger.error(mensaje)
        return resultado, mensaje
    except BusinessException as be:
        logger.error(f"Error de negocio en cargar_tc_gescom: {be}")
        mensaje = f"Error de negocio: {be}"
        resultado = False
    except Exception as e:
        logger.error(f"Error inesperado en cargar_tc_gescom: {e}")
        mensaje = f"Error inesperado: {e}"
        resultado = False
    finally:
        logger.info("Fin del proceso ...")

def bot_run(cfg, mensaje="Bot 06 - Gescom Cargar TC"):
    resultado = False
    try:
        logger.info(f"Iniciando {mensaje}")
        resultado = cargar_tc_gescom(cfg)
        mensaje = "Bot 06 - Gescom Cargar TC completado exitosamente"
        return resultado, mensaje
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
        resultado = False