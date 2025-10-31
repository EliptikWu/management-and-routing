"""
Script de prueba manual para verificar endpoints
Ejecutar: python tests/manual_test.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(name, response):
    """Helper para imprimir respuestas"""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def main():
    print("🧪 INICIANDO PRUEBAS MANUALES")
    
    # 1. Health check
    print_response(
        "1️⃣ Health Check",
        requests.get(f"{BASE_URL}/")
    )
    
    # 2. Crear orden
    nueva_orden = {
        "titulo": "Prueba Manual - Reseteo de contraseña",
        "descripcion": "El usuario necesita resetear su contraseña corporativa de forma urgente",
        "creador": "admin@empresa.com",
        "prioridad": "ALTA"
    }
    r_crear = requests.post(f"{BASE_URL}/ordenes/", json=nueva_orden)
    print_response("2️⃣ Crear Orden", r_crear)
    orden_id = r_crear.json()["id"]
    
    # 3. Listar órdenes
    print_response(
        "3️⃣ Listar Órdenes",
        requests.get(f"{BASE_URL}/ordenes/")
    )
    
    # 4. Obtener detalle de orden
    print_response(
        "4️⃣ Detalle de Orden",
        requests.get(f"{BASE_URL}/ordenes/{orden_id}")
    )
    
    # 5. Listar áreas disponibles
    print_response(
        "5️⃣ Listar Áreas",
        requests.get(f"{BASE_URL}/areas/")
    )
    
    # 6. Asignar áreas a la orden
    asignacion = {
        "area_ids": [1, 2],  # Soporte e Infraestructura
        "asignada_a": "Carlos Mendoza"
    }
    print_response(
        "6️⃣ Asignar Áreas",
        requests.post(f"{BASE_URL}/ordenes/{orden_id}/asignaciones", json=asignacion)
    )
    
    # 7. Cambiar estado parcial de un área
    cambio_estado = {
        "nuevo_estado": "EN_PROGRESO",
        "notas": "Iniciando trabajo en la orden"
    }
    print_response(
        "7️⃣ Cambiar Estado Parcial (Área 1)",
        requests.patch(f"{BASE_URL}/ordenes/{orden_id}/areas/1", json=cambio_estado)
    )
    
    # 8. Obtener historial
    print_response(
        "8️⃣ Historial de Orden",
        requests.get(f"{BASE_URL}/ordenes/{orden_id}/historial")
    )
    
    # 9. KPIs
    print_response(
        "9️⃣ KPIs del Sistema",
        requests.get(f"{BASE_URL}/kpis")
    )
    
    # 10. Filtrar órdenes por estado
    print_response(
        "🔟 Filtrar por Estado EN_PROGRESO",
        requests.get(f"{BASE_URL}/ordenes/?estado=EN_PROGRESO")
    )
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)


if __name__ == "__main__":
    main()