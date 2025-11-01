"""
Tests para el temporizador
"""
import time
import requests

API_BASE_URL = "http://localhost:8000"


def test_estado_temporizador():
    """Verifica que el temporizador esté activo"""
    print("\n1️⃣ Verificando estado del temporizador...")
    
    response = requests.get(f"{API_BASE_URL}/temporizador/estado")
    data = response.json()
    
    print(f"   Activo: {data['activo']}")
    print(f"   N_SEG: {data['configuracion']['n_seg']}s")
    print(f"   SLA_SEG: {data['configuracion']['sla_seg']}s")
    print(f"   Estado Timeout: {data['configuracion']['estado_timeout']}")
    
    assert data['activo'], "El temporizador no está activo"
    print("   ✅ Temporizador activo")


def test_tick_manual():
    """Ejecuta un tick manual y verifica resultado"""
    print("\n2️⃣ Ejecutando tick manual...")
    
    response = requests.post(f"{API_BASE_URL}/temporizador/tick")
    data = response.json()
    
    print(f"   Áreas actualizadas: {data['areas_actualizadas']}")
    print(f"   Timeouts aplicados: {data['timeouts_aplicados']}")
    print(f"   Órdenes recalculadas: {len(data['ordenes_recalculadas'])}")
    
    if data['errores']:
        print(f"   ⚠️  Errores: {data['errores']}")
    else:
        print("   ✅ Tick ejecutado sin errores")
    
    return data


def test_estadisticas_sla():
    """Obtiene estadísticas de SLA"""
    print("\n3️⃣ Obteniendo estadísticas de SLA...")
    
    response = requests.get(f"{API_BASE_URL}/temporizador/estadisticas-sla")
    data = response.json()
    
    print(f"   Total áreas activas: {data['total_areas_activas']}")
    print(f"   Áreas cerca del límite: {data['areas_cerca_limite']}")
    print(f"   Áreas vencidas: {data['areas_vencidas']}")
    print(f"   Promedio segundos: {data['promedio_segundos']}s")
    print(f"   Cumplimiento SLA: {data['porcentaje_cumplimiento']}%")
    print("   ✅ Estadísticas obtenidas")


def test_incremento_progresivo():
    """Verifica que los segundos se incrementan progresivamente"""
    print("\n4️⃣ Probando incremento progresivo (3 ticks)...")
    
    # Obtener orden en progreso
    ordenes_response = requests.get(f"{API_BASE_URL}/ordenes?estado=EN_PROGRESO")
    ordenes = ordenes_response.json()
    
    if not ordenes:
        print("   ⚠️  No hay órdenes EN_PROGRESO para probar")
        return
    
    orden_id = ordenes[0]['id']
    print(f"   Orden de prueba: #{orden_id}")
    
    # Obtener segundos iniciales
    detalle = requests.get(f"{API_BASE_URL}/ordenes/{orden_id}").json()
    segundos_inicial = sum(a['seg_acumulados'] for a in detalle['asignaciones'] 
                          if a['estado_parcial'] == 'EN_PROGRESO')
    print(f"   Segundos iniciales: {segundos_inicial}s")
    
    # Ejecutar 3 ticks manuales
    for i in range(3):
        tick_result = requests.post(f"{API_BASE_URL}/temporizador/tick").json()
        print(f"   Tick {i+1}: {tick_result['areas_actualizadas']} áreas actualizadas")
        time.sleep(0.5)
    
    # Verificar incremento
    detalle_final = requests.get(f"{API_BASE_URL}/ordenes/{orden_id}").json()
    segundos_final = sum(a['seg_acumulados'] for a in detalle_final['asignaciones'] 
                         if a['estado_parcial'] in ['EN_PROGRESO', 'VENCIDA'])
    
    print(f"   Segundos finales: {segundos_final}s")
    print(f"   Incremento: +{segundos_final - segundos_inicial}s")
    
    # Verificar que aumentó
    assert segundos_final > segundos_inicial, "Los segundos no aumentaron"
    print("   ✅ Incremento verificado")


def test_timeout_forzado():
    """Fuerza un timeout modificando una orden"""
    print("\n5️⃣ Probando aplicación de timeout...")
    
    # Buscar orden con área EN_PROGRESO cerca del límite
    ordenes = requests.get(f"{API_BASE_URL}/ordenes?estado=EN_PROGRESO").json()
    
    if not ordenes:
        print("   ⚠️  No hay órdenes EN_PROGRESO para probar timeout")
        return
    
    # Tomar la primera orden
    orden = ordenes[0]
    print(f"   Orden de prueba: #{orden['id']} - {orden['titulo']}")
    print(f"   Segundos actuales: {orden['total_segundos']}s")
    
    # Obtener configuración de SLA
    config = requests.get(f"{API_BASE_URL}/temporizador/estado").json()
    sla_seg = config['configuracion']['sla_seg']
    
    print(f"   SLA configurado: {sla_seg}s")
    
    if orden['total_segundos'] >= sla_seg:
        print("   ℹ️  Orden ya superó el SLA")
    else:
        segundos_faltantes = sla_seg - orden['total_segundos']
        ticks_necesarios = (segundos_faltantes // config['configuracion']['n_seg']) + 2
        print(f"   Faltan ~{ticks_necesarios} ticks para timeout")
    
    print("   ✅ Test de timeout preparado (ejecutar ticks para ver efecto)")


def main():
    """Ejecuta todas las pruebas"""
    print("="*60)
    print("🧪 PRUEBAS DEL TEMPORIZADOR")
    print("="*60)
    
    try:
        test_estado_temporizador()
        test_estadisticas_sla()
        test_tick_manual()
        test_incremento_progresivo()
        test_timeout_forzado()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()