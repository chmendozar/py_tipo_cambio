#!/usr/bin/env python3
"""
Test script para verificar las correcciones del bot de Bloomberg.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modulos.bot_01_tc_bloomberg import is_valid_exchange_rate, limpiar_tipo_cambio, extrer_tipo_cambio_bloomberg
from config.config import cargar_configuracion
import logging

# Configurar logging básico para las pruebas
logging.basicConfig(level=logging.INFO)

# Alias para get_config
def get_config():
    return cargar_configuracion()

def test_is_valid_exchange_rate():
    """Prueba la función de validación de tipo de cambio."""
    print("=== Probando is_valid_exchange_rate ===")
    
    # Casos válidos
    valid_cases = [
        "3.45",
        "3.50",
        "4.20",
        "USD 3.45",
        "3.45 PEN",
        "$3.45"
    ]
    
    # Casos inválidos
    invalid_cases = [
        "abc",
        "123",
        "3.456",  # Más de 2 decimales
        "0.5",    # Muy bajo
        "15.0",   # Muy alto
        "",       # Vacío
        None,     # None
        "3,45",   # Coma en lugar de punto
        "<jҽsPjIudlԁ7|"  # Texto corrupto
    ]
    
    print("Casos válidos:")
    for case in valid_cases:
        result = is_valid_exchange_rate(case)
        print(f"  '{case}' -> {result}")
        assert result, f"'{case}' debería ser válido"
    
    print("Casos inválidos:")
    for case in invalid_cases:
        result = is_valid_exchange_rate(case)
        print(f"  '{case}' -> {result}")
        assert not result, f"'{case}' debería ser inválido"
    
    print("✅ Todas las pruebas de validación pasaron")

def test_limpiar_tipo_cambio():
    """Prueba la función de limpieza de tipo de cambio."""
    print("\n=== Probando limpiar_tipo_cambio ===")
    
    # Casos válidos
    valid_cases = [
        ("3.45", 3.45),
        ("USD 3.45", 3.45),
        ("3.45 PEN", 3.45),
        ("$3.45", 3.45),
        ("3.50", 3.50)
    ]
    
    # Casos inválidos
    invalid_cases = [
        "abc",
        "123",
        "3.456",
        "0.5",
        "15.0",
        "",
        None,
        "3,45",
        "<jҽsPjIudlԁ7|"
    ]
    
    print("Casos válidos:")
    for input_val, expected in valid_cases:
        result = limpiar_tipo_cambio(input_val)
        print(f"  '{input_val}' -> {result} (esperado: {expected})")
        assert result == expected, f"'{input_val}' debería resultar en {expected}, pero obtuvo {result}"
    
    print("Casos inválidos:")
    for case in invalid_cases:
        result = limpiar_tipo_cambio(case)
        print(f"  '{case}' -> {result}")
        assert result is None, f"'{case}' debería resultar en None, pero obtuvo {result}"
    
    print("✅ Todas las pruebas de limpieza pasaron")

def test_bloomberg_extraction():
    """Prueba la extracción del tipo de cambio de Bloomberg"""
    try:
        print("=== PRUEBA DE EXTRACCIÓN DE BLOOMBERG ===")
        
        # Obtener configuración
        cfg = get_config()
        print(f"URL de Bloomberg: {cfg['fuentes_tc']['url_bloomberg']}")
        
        # Intentar extraer el tipo de cambio
        print("\nIniciando extracción...")
        tipo_cambio = extrer_tipo_cambio_bloomberg(cfg)
        
        if tipo_cambio:
            print(f"\n✅ ÉXITO: Tipo de cambio extraído: {tipo_cambio}")
            return True
        else:
            print("\n❌ ERROR: No se pudo extraer el tipo de cambio")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    try:
        test_is_valid_exchange_rate()
        test_limpiar_tipo_cambio()
        success = test_bloomberg_extraction()
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        sys.exit(1) 