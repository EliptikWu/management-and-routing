# Documentación de API - Enrutador de Órdenes

## Base URL
```
http://localhost:8000
```

## Autenticación
No implementada en MVP (todos los endpoints son públicos)

---

## Endpoints de Órdenes

### 1. Crear Orden
**POST** `/ordenes/`

**Request Body:**
```json
{
  "titulo": "Instalación de software en equipo nuevo",
  "descripcion": "Instalar Office 365, Adobe Reader y configurar VPN corporativa",
  "creador": "admin@empresa.com",
  "prioridad": "MEDIA"
}
```

**Response (201):**
```json
{
  "id": 1,
  "titulo": "Instalación de software en equipo nuevo",
  "descripcion": "Instalar Office 365...",
  "creador": "admin@empresa.com",
  "estado_global": "NUEVA",
  "prioridad": "MEDIA",
  "creada_en": "2025-10-31T10:30:00",
  "actualizada_en": "2025-10-31T10:30:00",
  "asignaciones": []
}
```

**Errores:**
- `400`: Datos inválidos
- `422`: Validación fallida

---

### 2. Listar Órdenes
**GET** `/ordenes/?estado={estado}&skip=0&limit=100`

**Query Params:**
- `estado` (opcional): Filtro por estado_global
- `skip`: Paginación (default: 0)
- `limit`: Límite de resultados (default: 100, max: 500)

**Response (200):**
```json
[
  {
    "id": 1,
    "titulo": "Instalación de software...",
    "estado_global": "EN_PROGRESO",
    "prioridad": "MEDIA",
    "creador": "admin@empresa.com",
    "num_areas": 2,
    "areas_completadas": 1,
    "total_segundos": 145,
    "creada_en": "2025-10-31T10:30:00",
    "actualizada_en": "2025-10-31T11:45:00"
  }
]
```

---

### 3. Obtener Detalle de Orden
**GET** `/ordenes/{orden_id}`

**Response (200):**
```json
{
  "id": 1,
  "titulo": "Instalación de software...",
  "estado_global": "EN_PROGRESO",
  "asignaciones": [
    {
      "id": 1,
      "area_id": 1,
      "area_nombre": "Soporte Técnico",
      "asignada_a": "Carlos Mendoza",
      "estado_parcial": "COMPLETADA",
      "seg_acumulados": 120,
      "asignada_en": "2025-10-31T10:35:00",
      "iniciada_en": "2025-10-31T10:40:00",
      "completada_en": "2025-10-31T12:00:00"
    }
  ]
}
```

**Errores:**
- `404`: Orden no encontrada

---

### 4. Asignar Áreas
**POST** `/ordenes/{orden_id}/asignaciones`

**Request Body:**
```json
{
  "area_ids": [1, 2, 3],
  "asignada_a": "Pedro Sánchez"
}
```

**Response (200):** Orden completa con nuevas asignaciones

**Errores:**
- `404`: Orden o áreas no encontradas
- `400`: Área ya asignada (duplicado)

---

### 5. Quitar Área
**DELETE** `/ordenes/{orden_id}/asignaciones/{area_id}`

**Response (200):** Orden actualizada

**Errores:**
- `404`: Asignación no encontrada

---

### 6. Cambiar Estado Parcial
**PATCH** `/ordenes/{orden_id}/areas/{area_id}`

**Request Body:**
```json
{
  "nuevo_estado": "EN_PROGRESO",
  "notas": "Iniciando diagnóstico del equipo"
}
```

**Estados válidos:**
- `EN_PROGRESO`
- `PENDIENTE`
- `COMPLETADA`
- `CERRADA_SIN_SOLUCION`
- `VENCIDA`

**Response (200):** Asignación actualizada

**Efectos secundarios:**
- Actualiza timestamps automáticamente
- Recalcula estado_global de la orden
- Registra evento en historial

---

### 7. Obtener Historial
**GET** `/ordenes/{orden_id}/historial`

**Response (200):**
```json
[
  {
    "id": 15,
    "orden_id": 1,
    "evento": "CAMBIO_ESTADO_PARCIAL",
    "detalle": "Área Soporte Técnico: ASIGNADA → EN_PROGRESO",
    "estado_global": "EN_PROGRESO",
    "timestamp": "2025-10-31T11:30:00",
    "actor": "Carlos Mendoza"
  },
  {
    "id": 14,
    "orden_id": 1,
    "evento": "AREA_ASIGNADA",
    "detalle": "Área asignada: Soporte Técnico → Carlos Mendoza",
    "estado_global": null,
    "timestamp": "2025-10-31T10:35:00",
    "actor": "SISTEMA"
  }
]
```

---

## Endpoints de Áreas

### 8. Listar Áreas
**GET** `/areas/?activo=true`

**Response (200):**
```json
[
  {
    "id": 1,
    "nombre": "Soporte Técnico",
    "responsable": "Carlos Mendoza",
    "contacto": "cmendoza@empresa.com",
    "activo": true,
    "creada_en": "2025-10-30T00:00:00"
  }
]
```

---

## Endpoint de KPIs

### 9. Obtener KPIs
**GET** `/kpis`

**Response (200):**
```json
{
  "total_ordenes": 25,
  "completadas": 18,
  "pendientes": 5,
  "cerradas_sin_solucion": 2
}
```

---

## Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación fallida |
| 500 | Internal Server Error - Error del servidor |

---

## Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc