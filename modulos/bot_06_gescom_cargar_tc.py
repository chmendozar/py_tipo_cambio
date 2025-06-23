import logging
from utilidades.excepciones import BusinessException
import variables_globales as vg

logger = logging.getLogger("Bot 06 - Gescom Cargar TC")

def bot_run(cfg, mensaje="Bot 06 - Gescom Cargar TC"):
    resultado = False
    try:
        logger.info(f"Iniciando {mensaje}")
        resultado = True
        mensaje = "Bot 06 - Gescom Cargar TC completado exitosamente"
        return resultado, mensaje
    except BusinessException as be:
        logger.error(f"Error de negocio en bot_run: {be}")
        mensaje = f"Error de negocio: {be}"
        resultado = False