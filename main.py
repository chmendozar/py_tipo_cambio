import logging
import traceback
import platform
import os
import psutil
import variables_globales as vg
from utilidades.limpieza import cerrarProcesos as Limpieza
from modulos.bot_00_configuracion import bot_run as Bot_00_Configuracion
from modulos.bot_01_tc_bloomberg import bot_run as Bot_01_Bloomberg
from modulos.bot_02_calcular_tc import bot_run as Bot_02_CalcularTC
from modulos.bot_03_super_admin import bot_run as Bot_03_SuperAdmin
from modulos.bot_04_modulo_tc import bot_run as Bot_04_ModuloTC
from modulos.bot_05_tc_sbs import bot_run as Bot_05_TC_SBS
#from modulos.bot_06_tc_paypal import bot_run as Bot_06_TC_Paypal
from utilidades.notificaiones_whook import WebhookNotifier
from datetime import datetime


logger = logging.getLogger("Main - Orquestador")

def obtener_info_sistema():
    """
    Recopila información del sistema para diagnóstico.

    Returns:
        dict: Información básica del sistema
    """
    try:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "memory": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
            "cpu_count": os.cpu_count(),
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "available_memory": f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB"
        }
        return info
    except Exception as e:
        logger.warning(f"No se pudo obtener información completa del sistema: {e}")
        return {"error": str(e)}


def main():
    inicio = datetime.now()
    
    # Limpieza de ambiente
    lista_procesos = ["chrome.exe", "firefox.exe"]
    Limpieza(lista_procesos)

    logger.info(f"==================== INICIO DE ORQUESTACIÓN ====================")
    logger.info(f"Inicio de orquestación - {inicio.strftime('%Y-%m-%d %H:%M:%S')}")

    # Recopilar información del sistema
    info_sistema = obtener_info_sistema()
    logger.info(f"Información del sistema: {info_sistema}")
    notificaion = WebhookNotifier(cfg["webhooks"]["webhook_url"])

    try:
        # Configuración del bot
        logger.info("Cargando configuración del sistema...")
        cfg = Bot_00_Configuracion()
        if not cfg:
            logger.error("Error al cargar la configuración. Abortando proceso.")
            vg.system_exception = True
            return

        logger.info(f"Configuración cargada exitosamente. Secciones disponibles: {', '.join(cfg.keys())}")
        
        # Notificación de inicio
        #notificaion.send_notification("Inicio del proceso tipo de cambio PayPal")

        # Ejecución de los bots
        for bot_name, bot_function in [
            ("Bot 01 - Obtener TC bloomberg", Bot_01_Bloomberg),   
            ("Bot 02 - Calcular TC", Bot_02_CalcularTC),
            ("Bot 03 - Super Admin", Bot_03_SuperAdmin),
            ("Bot 04 - Registrar TC", Bot_04_ModuloTC),
            #("Bot 05 - Tipo cambio sbs", Bot_05_TC_SBS),
        ]:
            logger.info(f"==================== INICIANDO {bot_name} ====================")
            resultado, mensaje = bot_function(cfg)
            
            if resultado:
                logger.info(f"{bot_name} completado exitosamente: {mensaje}")
                if bot_name == "Bot 03 - Super Admin":
                    notificaion.send_notification(
                        f"Se registró tipo de cambio PayPal. Brecha: {cfg['valores']['brecha']} - "
                        f"TC Bloomberg: {vg.tipo_cambio_bloomberg} - "
                        f"TC Venta: {vg.tipo_cambio_venta} - "
                        f"TC Compra: {vg.tipo_cambio_compra}"
                    )  
                if bot_name == "Bot 04 - Registrar TC":
                    notificaion.send_notification(
                        "Se registró tipo de cambio ModuloTC\n"
                        f"TC Bloomberg: {vg.tipo_cambio_bloomberg}\n"
                        f"TC Compra: {vg.tipo_cambio_compra}\n"
                        f"TC Venta: {vg.tipo_cambio_venta}"
                    )   
                    
            else:
                logger.error(f"{bot_name} falló: {mensaje}")
                return
        
        # Verificar si hay excepciones de negocio o sistema
        if vg.business_exception:
            logger.info("Enviando Notificación por Error de Negocio...")
            return

        if vg.system_exception:
            logger.info("Enviando Notificación por Error de Sistema...")
            return

    except Exception as e:
        logger.error(f"Error en main: {e}")
        logger.error(traceback.format_exc())
        notificaion = WebhookNotifier(cfg["webhooks"]["webhook_exception"])
        notificaion.send_notification(
            f"Error: {traceback.extract_tb(e.__traceback__)[-1].filename}: {str(e)}"
        )

    finally:
        # Calcular tiempo total de ejecución
        fin = datetime.now()
        tiempo_total = fin - inicio
        logger.info(f"==================== FIN DE ORQUESTACIÓN ====================")
        logger.info(f"Fin de orquestación - {fin.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Tiempo total de ejecución: {tiempo_total}")
        
        # Notificación de fin
        #notificaion.send_notification(f"Fin del proceso de orquestación. Tiempo total de ejecución: {tiempo_total}")
        logger.info("Fin del proceso ...")


if __name__ == "__main__":
    main()