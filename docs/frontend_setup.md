# Guía de Integración - Frontend

## 🚀 Configuración Rápida

### 1. Verificar estructura de archivos

Asegúrate de que la carpeta `src/static/` tenga esta estructura:
```
src/static/
├── index.html
├── css/
│   └── styles.css
└── js/
    └── ordenes.js
```

### 2. Ejecutar el backend
```bash
python src/main.py
```

El servidor estará en: `http://localhost:8000`

### 3. Acceder a la aplicación

Abre tu navegador en una de estas URLs:

- **Frontend**: http://localhost:8000/static/index.html
- **Ruta directa**: http://localhost:8000/app
- **API Docs**: http://localhost:8000/docs

## 🧪 Pruebas

### Verificar conectividad

1. Abre la consola del navegador (F12)
2. Deberías ver: `🚀 Inicializando aplicación...`
3. Si hay errores de CORS, verifica que `CORS_ORIGINS` en `.env` incluya el origen

### Datos de prueba

Si ves "No hay órdenes disponibles":
1. Verifica que la base de datos tenga datos: `mysql -u root -p ordenes_multiarea -e "SELECT COUNT(*) FROM ordenes;"`
2. Ejecuta el seed si es necesario: `mysql -u root -p < db/seeds/seed_data.sql`

### Filtros

1. Selecciona un estado en el dropdown
2. La lista se filtrará automáticamente sin recargar la página
3. Los KPIs no cambian (muestran totales globales)

## 🎨 Personalización

### Cambiar colores

Edita las variables CSS en `styles.css`:
```css
:root {
    --color-primary: #2563eb;  /* Azul principal */
    --color-success: #16a34a;  /* Verde éxito */
    --color-warning: #ea580c;  /* Naranja advertencia */
    --color-danger: #dc2626;   /* Rojo error */
}
```

### Cambiar URL del API

Edita `ordenes.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000'; // Cambiar si usas otro puerto
```

### Activar auto-refresh

Descomenta la última línea de `ordenes.js`:
```javascript
// Refrescar cada 30 segundos
iniciarAutoRefresh(30);
```

## 📱 Responsive Design

La aplicación se adapta automáticamente:

- **Desktop (>768px)**: Tabla completa
- **Mobile (≤768px)**: Cards compactos
- **KPIs**: Grid adaptativo 4→2→1 columnas

## ♿ Accesibilidad

- ✅ Atributos ARIA (labels, roles, live regions)
- ✅ Navegación por teclado (Tab, Enter)
- ✅ Contraste WCAG AA
- ✅ Textos alternativos
- ✅ Focus visible

## 🐛 Troubleshooting

### "No se pudieron cargar los KPIs"

**Causa**: Backend no está corriendo o CORS bloqueado

**Solución**:
1. Verificar que `python src/main.py` esté activo
2. Revisar `.env` → `CORS_ORIGINS` debe incluir `http://localhost:8000`

### "No hay órdenes disponibles" (pero hay datos)

**Causa**: Error en la consulta al API

**Solución**:
1. Abrir DevTools → Network
2. Verificar que `GET /ordenes` retorne 200
3. Si retorna 500, revisar logs del backend

### Estilos no cargan

**Causa**: Ruta incorrecta

**Solución**:
- Verificar que `styles.css` esté en `src/static/css/`
- Ruta en HTML debe ser: `<link rel="stylesheet" href="css/styles.css">`

## 🚀 Próximos Pasos (E6)

El siguiente entregable agregará:
- Vista de detalle de orden
- Acciones (iniciar, pausar, completar)
- Historial de eventos
- Formulario de crear/editar orden
```

---

## ✅ Cumplimiento de Criterios E5

| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| **KPIs (4 métricas)** | ✅ | Total, Completadas, Pendientes, Sin Solución |
| **Filtro reactivo** | ✅ | Dropdown con recarga automática sin reload |
| **Responsivo** | ✅ | Tabla (desktop) + Cards (mobile) |
| **Accesible** | ✅ | ARIA labels, roles, tabindex, focus visible |
| **Datos reales** | ✅ | Consume API `/ordenes` y `/kpis` |
| **KPIs correctos** | ✅ | Valores calculados desde endpoint `/kpis` |
| **Sin frameworks** | ✅ | Vanilla JS + CSS puro |

---

## 🎨 Capturas de Pantalla (Descripción)

### Desktop View
```
┌─────────────────────────────────────────────┐
│  Sistema de Gestión de Órdenes             │
│  [KPI Total] [KPI ✅] [KPI ⏳] [KPI ❌]     │
│  ┌──────────────────────────────────────┐  │
│  │ Filtrar: [Dropdown ▼] [🔄][➕]      │  │
│  └──────────────────────────────────────┘  │
│  Órdenes de Trabajo              [8 órdenes]│
│  ┌────────────────────────────────────────┐│
│  │ ID│Título│Estado│Prioridad│Áreas│...  ││
│  │ 1 │Insta│✅    │Media    │2/2  │...  ││
│  │ 2 │Bug  │⏳    │Alta     │1/1  │...  ││
│  └────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### Mobile View
```
┌─────────────────┐
│ [KPI][KPI]      │
│ [KPI][KPI]      │
│ Filtrar: [▼]    │
│ [🔄] [➕]       │
│ ┌─────────────┐ │
│ │ #1 [Media]  │ │
│ │ Instalación │ │
│ │ ✅ Completada│ │
│ │ Áreas: 2/2  │ │
│ │ [Ver Detalle]│ │
│ └─────────────┘ │
│ ┌─────────────┐ │
│ │ #2 ...      │ │
│ └─────────────┘ │
└─────────────────┘