# Py Tipo Cambio - Sistema de Automatización de Tipo de Cambio

Sistema automatizado para la obtención, cálculo y registro de tipos de cambio desde múltiples fuentes, incluyendo Bloomberg, con integración a sistemas administrativos.

## 📋 Descripción

Este proyecto automatiza el proceso completo de obtención y registro de tipos de cambio USD/PEN desde diversas fuentes financieras, incluyendo:

- **Bloomberg** (fuente principal)
- Exchange Rate API
- XE.com
- Investing.com
- BCRP (Banco Central de Reserva del Perú)
- Google Finance

El sistema calcula automáticamente los tipos de cambio de compra y venta aplicando márgenes configurables y registra los resultados en sistemas administrativos como SuperAdmin y MóduloTC.

## 🏗️ Arquitectura

El sistema está organizado en módulos especializados:

```
py_tipo_cambio/
├── main.py                 # Orquestador principal
├── modulos/               # Módulos especializados
│   ├── bot_00_configuracion.py    # Configuración del sistema
│   ├── bot_01_tc_bloomberg.py     # Obtención TC desde Bloomberg
│   ├── bot_02_calcular_tc.py      # Cálculo de TC compra/venta
│   ├── bot_03_super_admin.py      # Registro en SuperAdmin
│   └── bot_04_modulo_tc.py        # Registro en MóduloTC
├── utilidades/            # Utilidades del sistema
├── config/               # Configuración
├── cliente/              # Directorios de entrada/salida
├── logs/                 # Logs del sistema
└── ejemplos/             # Ejemplos de uso
```

## 🚀 Características

- ✅ **Automatización completa** del proceso de tipo de cambio
- ✅ **Múltiples fuentes** de datos financieros
- ✅ **Cálculo automático** de márgenes de compra/venta
- ✅ **Integración** con sistemas administrativos
- ✅ **Notificaciones** vía webhook (Google Chat)
- ✅ **Logging detallado** de todas las operaciones
- ✅ **Manejo robusto de errores** y reintentos
- ✅ **Configuración flexible** via archivos INI
- ✅ **Docker support** para despliegue containerizado

## 📦 Instalación

### Requisitos Previos

- Python 3.8+
- Chrome/Firefox (para web scraping)
- Acceso a APIs de Bloomberg (configurable)

### Instalación Local

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd py_tipo_cambio
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar el sistema:**
```bash
cp config/config.ini.example config/config.ini
# Editar config/config.ini con tus credenciales
```

### Instalación con Docker

1. **Construir y ejecutar con Docker Compose:**
```bash
# Para producción
docker-compose up -d

# Para desarrollo
docker-compose --profile dev up -d
```

2. **Ejecutar manualmente:**
```bash
docker build -t py-tipo-cambio .
docker run -v $(pwd)/config:/app/config py-tipo-cambio
```

## ⚙️ Configuración

### Archivo de Configuración (`config/config.ini`)

```ini
[general]
nombre_bot = tipo_cambio
version = 1.0

[valores]
brecha = 3.0          # Margen aplicado al tipo de cambio
inicial = 3.0         # Valor inicial
final = 5.0           # Valor final

[api]
api_modulo_login = "https://modulotc.ligo.live/api/auth"
api_modulo_tc_add = "https://modulotc.ligo.live/api/exchange_rate_date/add"

[webhooks]
webhook_url = "https://chat.googleapis.com/v1/spaces/..."
```

### Variables de Entorno

- `PYTHONUNBUFFERED=1` - Para logging en tiempo real
- `DISPLAY=:99` - Para navegadores headless

## 🎯 Uso

### Ejecución Básica

```bash
python main.py
```

### Ejecución con Docker

```bash
# Ejecutar el contenedor
docker-compose up

# Ver logs
docker-compose logs -f py-tipo-cambio
```

### Ejemplo de Uso del Cliente HTTP

```python
from utilidades.httpclient import get_http_client

# Obtener cliente HTTP
http_client = get_http_client()

# Realizar petición
response = http_client.make_request("https://api.example.com/data")

if response:
    print(f"Éxito: {response.status_code}")
    data = response.json()
else:
    print("Error en la petición")
```

## 📊 Flujo de Trabajo

1. **Configuración** - Carga configuración del sistema
2. **Obtención Bloomberg** - Scraping del tipo de cambio desde Bloomberg
3. **Cálculo TC** - Aplicación de márgenes para compra/venta
4. **Registro SuperAdmin** - Registro en sistema administrativo
5. **Registro MóduloTC** - Registro en módulo de tipo de cambio
6. **Notificaciones** - Envío de notificaciones vía webhook

## 🔧 Desarrollo

### Estructura de Módulos

Cada módulo sigue el patrón:
```python
def bot_run(config):
    """
    Función principal del módulo
    
    Args:
        config: Configuración del sistema
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Lógica del módulo
        return True, "Operación exitosa"
    except Exception as e:
        return False, f"Error: {str(e)}"
```

### Agregar Nuevas Fuentes de TC

1. Crear nuevo módulo en `modulos/`
2. Agregar URL en `config/config.ini`
3. Integrar en el orquestador `main.py`

## 📝 Logging

El sistema genera logs detallados en `logs/` con formato:
```
log_YYYYMMDD_HHMMSS.log
```

Ejemplo de log:
```
2025-01-22 19:45:15 - Main - Orquestador - INFO - ==================== INICIO DE ORQUESTACIÓN ====================
2025-01-22 19:45:15 - Main - Orquestador - INFO - Inicio de orquestación - 2025-01-22 19:45:15
```

## 🔔 Notificaciones

El sistema envía notificaciones automáticas vía:
- **Google Chat Webhook** - Para alertas en tiempo real
- **Email** - Para reportes detallados (configurable)

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest test/

# Test específico
python test/test_bloomberg_fix.py
```

## 📁 Estructura de Directorios

```
cliente/
├── input/          # Archivos de entrada
└── output/         # Archivos generados

config/
├── config.ini      # Configuración principal
└── config.py       # Cargador de configuración

logs/               # Logs del sistema

modulos/            # Módulos especializados

utilidades/         # Utilidades del sistema
├── httpclient.py   # Cliente HTTP avanzado
├── logger.py       # Sistema de logging
├── notificaciones_mail.py
└── notificaiones_whook.py
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Revisar los logs en `logs/`
- Verificar configuración en `config/config.ini`
- Consultar ejemplos en `ejemplos/`

## 🔄 Changelog

### v1.0
- Sistema base de automatización
- Integración con Bloomberg
- Registro en sistemas administrativos
- Notificaciones vía webhook
- Soporte Docker

---
