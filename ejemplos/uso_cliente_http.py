"""
Ejemplo de uso del cliente HTTP mejorado para el bot de tipo de cambio.
Este archivo demuestra las diferentes formas de usar el cliente HTTP avanzado.
"""

import logging
import time
from utilidades.httpclient import get_http_client, create_http_client, AdvancedHTTPClient

# Configurar logging para ver los detalles
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def ejemplo_uso_basico():
    """Ejemplo básico de uso del cliente HTTP."""
    print("=== Ejemplo de Uso Básico ===")
    
    # Obtener cliente HTTP por defecto
    http_client = get_http_client()
    
    # Realizar petición simple
    response = http_client.make_request("https://httpbin.org/get")
    
    if response:
        print(f"✅ Petición exitosa: {response.status_code}")
        print(f"   Tamaño de respuesta: {len(response.content)} bytes")
    else:
        print("❌ Petición falló")

def ejemplo_uso_con_context_manager():
    """Ejemplo usando context manager para manejo automático de sesión."""
    print("\n=== Ejemplo con Context Manager ===")
    
    with get_http_client().session_context() as client:
        # Realizar múltiples peticiones
        urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/404"
        ]
        
        for url in urls:
            response = client.make_request(url)
            if response:
                print(f"✅ {url}: {response.status_code}")
            else:
                print(f"❌ {url}: Falló")
    
    print("   Sesión cerrada automáticamente")

def ejemplo_cliente_personalizado():
    """Ejemplo de cliente HTTP con configuración personalizada."""
    print("\n=== Ejemplo de Cliente Personalizado ===")
    
    # Crear cliente con configuración específica
    custom_client = create_http_client(
        max_retries=2,
        timeout=5,
        pool_connections=5,
        pool_maxsize=10,
        rate_limit_min=0.5,
        rate_limit_max=1.5,
        verify_ssl=True
    )
    
    # Realizar petición con cliente personalizado
    response = custom_client.make_request("https://httpbin.org/delay/2")
    
    if response:
        print(f"✅ Petición con cliente personalizado: {response.status_code}")
    else:
        print("❌ Petición con cliente personalizado falló")
    
    # Mostrar información de la sesión
    session_info = custom_client.get_session_info()
    print(f"   Información de sesión: {session_info}")
    
    # Cerrar cliente
    custom_client.close()

def ejemplo_manejo_errores():
    """Ejemplo de manejo de diferentes tipos de errores."""
    print("\n=== Ejemplo de Manejo de Errores ===")
    
    http_client = get_http_client()
    
    # URLs que generarán diferentes tipos de errores
    test_urls = [
        "https://httpbin.org/status/500",  # Error del servidor
        "https://httpbin.org/status/404",  # No encontrado
        "https://httpbin.org/delay/10",    # Timeout
        "https://invalid-domain-12345.com", # Error de DNS
        "https://httpbin.org/status/200"   # Éxito
    ]
    
    for url in test_urls:
        print(f"\nProbando: {url}")
        start_time = time.time()
        
        response = http_client.make_request(url, timeout=3)
        
        elapsed_time = time.time() - start_time
        
        if response:
            print(f"   ✅ Éxito: {response.status_code} ({elapsed_time:.2f}s)")
        else:
            print(f"   ❌ Falló: ({elapsed_time:.2f}s)")

def ejemplo_headers_personalizados():
    """Ejemplo de uso de headers personalizados."""
    print("\n=== Ejemplo de Headers Personalizados ===")
    
    http_client = get_http_client()
    
    # Headers personalizados
    custom_headers = {
        "User-Agent": "MiBot/1.0 (Tipo Cambio Scraper)",
        "Accept": "application/json",
        "X-Custom-Header": "valor-personalizado"
    }
    
    # Realizar petición con headers personalizados
    response = http_client.make_request(
        "https://httpbin.org/headers",
        headers=custom_headers
    )
    
    if response:
        print(f"✅ Petición con headers personalizados: {response.status_code}")
        # Mostrar los headers que recibió el servidor
        data = response.json()
        print(f"   Headers recibidos: {data.get('headers', {})}")
    else:
        print("❌ Petición con headers personalizados falló")

def ejemplo_rate_limiting():
    """Ejemplo de rate limiting automático."""
    print("\n=== Ejemplo de Rate Limiting ===")
    
    http_client = get_http_client()
    
    print("Realizando 5 peticiones consecutivas (rate limiting automático):")
    
    for i in range(5):
        start_time = time.time()
        
        response = http_client.make_request("https://httpbin.org/get")
        
        elapsed_time = time.time() - start_time
        
        if response:
            print(f"   Petición {i+1}: ✅ ({elapsed_time:.2f}s)")
        else:
            print(f"   Petición {i+1}: ❌ ({elapsed_time:.2f}s)")

def ejemplo_comparacion_clientes():
    """Ejemplo comparando diferentes configuraciones de cliente."""
    print("\n=== Ejemplo de Comparación de Clientes ===")
    
    # Cliente rápido (poco rate limiting)
    fast_client = create_http_client(
        rate_limit_min=0.1,
        rate_limit_max=0.3,
        timeout=5
    )
    
    # Cliente lento (más rate limiting)
    slow_client = create_http_client(
        rate_limit_min=2.0,
        rate_limit_max=4.0,
        timeout=10
    )
    
    urls = ["https://httpbin.org/get"] * 3
    
    print("Cliente rápido:")
    start_time = time.time()
    for url in urls:
        response = fast_client.make_request(url)
        if response:
            print(f"   ✅ {response.status_code}")
        else:
            print("   ❌ Falló")
    fast_time = time.time() - start_time
    
    print(f"Cliente lento:")
    start_time = time.time()
    for url in urls:
        response = slow_client.make_request(url)
        if response:
            print(f"   ✅ {response.status_code}")
        else:
            print("   ❌ Falló")
    slow_time = time.time() - start_time
    
    print(f"\nTiempo cliente rápido: {fast_time:.2f}s")
    print(f"Tiempo cliente lento: {slow_time:.2f}s")
    
    # Cerrar clientes
    fast_client.close()
    slow_client.close()

def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("🚀 Ejemplos de Uso del Cliente HTTP Mejorado")
    print("=" * 50)
    
    try:
        ejemplo_uso_basico()
        ejemplo_uso_con_context_manager()
        ejemplo_cliente_personalizado()
        ejemplo_manejo_errores()
        ejemplo_headers_personalizados()
        ejemplo_rate_limiting()
        ejemplo_comparacion_clientes()
        
        print("\n" + "=" * 50)
        print("✅ Todos los ejemplos completados exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 