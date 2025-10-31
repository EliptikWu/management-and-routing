/**
 * ============================================
 * Enrutador de Órdenes - Frontend JavaScript
 * ============================================
 */

// Configuración
const API_BASE_URL = 'http://localhost:8000';
let ordenesData = [];
let kpisData = {};

// ============================================
// Inicialización
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    console.log('🚀 Inicializando aplicación...');
    cargarKPIs();
    cargarOrdenes();
}

// ============================================
// Event Listeners
// ============================================
function setupEventListeners() {
    // Filtro de estado
    const estadoFilter = document.getElementById('estado-filter');
    estadoFilter.addEventListener('change', (e) => {
        const estado = e.target.value;
        cargarOrdenes(estado);
    });

    // Botón de actualizar
    const btnRefresh = document.getElementById('btn-refresh');
    btnRefresh.addEventListener('click', () => {
        const estadoActual = document.getElementById('estado-filter').value;
        cargarKPIs();
        cargarOrdenes(estadoActual);
    });

    // Botón de nueva orden (placeholder)
    const btnNuevaOrden = document.getElementById('btn-nueva-orden');
    btnNuevaOrden.addEventListener('click', () => {
        alert('Funcionalidad de crear orden se implementará en siguiente entregable');
    });
}

// ============================================
// Carga de Datos
// ============================================
async function cargarKPIs() {
    try {
        const response = await fetch(`${API_BASE_URL}/kpis`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        kpisData = await response.json();
        renderizarKPIs(kpisData);
        
    } catch (error) {
        console.error('❌ Error al cargar KPIs:', error);
        mostrarError('No se pudieron cargar los KPIs. Verifica que el servidor esté corriendo.');
    }
}

async function cargarOrdenes(estado = '') {
    mostrarLoading(true);
    ocultarError();

    try {
        const url = estado 
            ? `${API_BASE_URL}/ordenes?estado=${encodeURIComponent(estado)}`
            : `${API_BASE_URL}/ordenes`;

        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        ordenesData = await response.json();
        renderizarOrdenes(ordenesData);
        
    } catch (error) {
        console.error('❌ Error al cargar órdenes:', error);
        mostrarError('No se pudieron cargar las órdenes. Verifica que el servidor esté corriendo en http://localhost:8000');
        renderizarOrdenes([]);
    } finally {
        mostrarLoading(false);
    }
}

// ============================================
// Renderizado de KPIs
// ============================================
function renderizarKPIs(kpis) {
    const elementos = {
        'total-ordenes': kpis.total_ordenes || 0,
        'completadas': kpis.completadas || 0,
        'pendientes': kpis.pendientes || 0,
        'sin-solucion': kpis.cerradas_sin_solucion || 0
    };

    for (const [id, valor] of Object.entries(elementos)) {
        const elemento = document.getElementById(id);
        if (elemento) {
            animarNumero(elemento, valor);
        }
    }
}

function animarNumero(elemento, valorFinal) {
    const valorInicial = parseInt(elemento.textContent) || 0;
    const duracion = 500; // ms
    const pasos = 20;
    const incremento = (valorFinal - valorInicial) / pasos;
    let pasoActual = 0;

    const intervalo = setInterval(() => {
        pasoActual++;
        const valorActual = Math.round(valorInicial + (incremento * pasoActual));
        elemento.textContent = valorActual;

        if (pasoActual >= pasos) {
            clearInterval(intervalo);
            elemento.textContent = valorFinal;
        }
    }, duracion / pasos);
}

// ============================================
// Renderizado de Órdenes
// ============================================
function renderizarOrdenes(ordenes) {
    // Actualizar contador
    const countBadge = document.getElementById('ordenes-count');
    countBadge.textContent = `${ordenes.length} ${ordenes.length === 1 ? 'orden' : 'órdenes'}`;

    // Mostrar/ocultar empty state
    const emptyState = document.getElementById('empty-state');
    const tableResponsive = document.querySelector('.table-responsive');
    const ordenesCards = document.getElementById('ordenes-cards');

    if (ordenes.length === 0) {
        emptyState.hidden = false;
        tableResponsive.style.display = 'none';
        ordenesCards.style.display = 'none';
    } else {
        emptyState.hidden = true;
        tableResponsive.style.display = 'block';
        
        // Renderizar tabla (desktop)
        renderizarTabla(ordenes);
        
        // Renderizar cards (mobile)
        renderizarCards(ordenes);
    }
}

function renderizarTabla(ordenes) {
    const tbody = document.getElementById('ordenes-tbody');
    tbody.innerHTML = '';

    ordenes.forEach(orden => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>#${orden.id}</strong></td>
            <td>
                <div style="max-width: 300px;">
                    <strong>${escapeHtml(orden.titulo)}</strong>
                    <div style="font-size: 0.75rem; color: var(--color-gray-600); margin-top: 0.25rem;">
                        ${escapeHtml(orden.creador)}
                    </div>
                </div>
            </td>
            <td>${renderEstadoBadge(orden.estado_global)}</td>
            <td>${renderPrioridadBadge(orden.prioridad)}</td>
            <td>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-weight: 600;">${orden.areas_completadas}/${orden.num_areas}</span>
                    <div style="flex: 1; background: var(--color-gray-200); height: 6px; border-radius: 3px; overflow: hidden; min-width: 60px;">
                        <div style="
                            width: ${calcularPorcentaje(orden.areas_completadas, orden.num_areas)}%;
                            height: 100%;
                            background: var(--color-success);
                            transition: width 0.3s;
                        "></div>
                    </div>
                </div>
            </td>
            <td>
                <span style="font-weight: 600; font-family: monospace;">
                    ${formatearSegundos(orden.total_segundos)}
                </span>
            </td>
            <td style="font-size: 0.75rem; color: var(--color-gray-600);">
                ${formatearFecha(orden.actualizada_en)}
            </td>
            <td>
                <button 
                    class="btn btn-primary" 
                    style="padding: 0.25rem 0.75rem; font-size: 0.75rem;"
                    onclick="verDetalle(${orden.id})"
                    aria-label="Ver detalle de orden ${orden.id}"
                >
                    Ver Detalle
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderizarCards(ordenes) {
    const container = document.getElementById('ordenes-cards');
    container.innerHTML = '';

    ordenes.forEach(orden => {
        const card = document.createElement('div');
        card.className = 'orden-card';
        card.innerHTML = `
            <div class="orden-card-header">
                <span class="orden-card-id">#${orden.id}</span>
                ${renderPrioridadBadge(orden.prioridad)}
            </div>
            <h3 class="orden-card-title">${escapeHtml(orden.titulo)}</h3>
            <div class="orden-card-meta">
                ${renderEstadoBadge(orden.estado_global)}
                <span style="font-size: 0.75rem; color: var(--color-gray-600);">
                    ${escapeHtml(orden.creador)}
                </span>
            </div>
            <div class="orden-card-stats">
                <div class="stat-item">
                    <span class="stat-label">Áreas</span>
                    <span class="stat-value">${orden.areas_completadas}/${orden.num_areas}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Tiempo</span>
                    <span class="stat-value">${formatearSegundos(orden.total_segundos)}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Actualizado</span>
                    <span class="stat-value">${formatearFechaCorta(orden.actualizada_en)}</span>
                </div>
            </div>
            <button 
                class="btn btn-primary" 
                style="width: 100%;"
                onclick="verDetalle(${orden.id})"
                aria-label="Ver detalle de orden ${orden.id}"
            >
                Ver Detalle
            </button>
        `;
        container.appendChild(card);
    });
}

// ============================================
// Helpers de Renderizado
// ============================================
function renderEstadoBadge(estado) {
    const estadosMap = {
        'NUEVA': { label: 'Nueva', class: 'nueva' },
        'ASIGNADA': { label: 'Asignada', class: 'asignada' },
        'EN_PROGRESO': { label: 'En Progreso', class: 'en_progreso' },
        'PENDIENTE': { label: 'Pendiente', class: 'pendiente' },
        'COMPLETADA': { label: 'Completada', class: 'completada' },
        'CERRADA_SIN_SOLUCION': { label: 'Sin Solución', class: 'cerrada_sin_solucion' },
        'VENCIDA': { label: 'Vencida', class: 'vencida' }
    };

    const config = estadosMap[estado] || { label: estado, class: 'nueva' };
    return `<span class="estado-badge estado-${config.class}">${config.label}</span>`;
}

function renderPrioridadBadge(prioridad) {
    const prioridadesMap = {
        'BAJA': { label: 'Baja', class: 'baja' },
        'MEDIA': { label: 'Media', class: 'media' },
        'ALTA': { label: 'Alta', class: 'alta' },
        'CRITICA': { label: 'Crítica', class: 'critica' }
    };

    const config = prioridadesMap[prioridad] || { label: prioridad, class: 'media' };
    return `<span class="prioridad-badge prioridad-${config.class}">${config.label}</span>`;
}

// ============================================
// Utilidades
// ============================================
function formatearSegundos(segundos) {
    if (!segundos || segundos === 0) return '0s';
    
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segs = segundos % 60;

    if (horas > 0) {
        return `${horas}h ${minutos}m`;
    } else if (minutos > 0) {
        return `${minutos}m ${segs}s`;
    } else {
        return `${segs}s`;
    }
}

function formatearFecha(fechaISO) {
    const fecha = new Date(fechaISO);
    const ahora = new Date();
    const diffMs = ahora - fecha;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHoras = Math.floor(diffMs / 3600000);
    const diffDias = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Hace un momento';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHoras < 24) return `Hace ${diffHoras} h`;
    if (diffDias < 7) return `Hace ${diffDias} días`;

    return fecha.toLocaleDateString('es-CO', { 
        day: '2-digit', 
        month: 'short',
        year: 'numeric'
    });
}

function formatearFechaCorta(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-CO', { 
        day: '2-digit', 
        month: '2-digit'
    });
}

function calcularPorcentaje(completadas, total) {
    if (total === 0) return 0;
    return Math.round((completadas / total) * 100);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function mostrarLoading(mostrar) {
    const loading = document.getElementById('loading');
    loading.hidden = !mostrar;
}

function mostrarError(mensaje) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = `⚠️ ${mensaje}`;
    errorDiv.hidden = false;
}

function ocultarError() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.hidden = true;
}

// ============================================
// Acciones
// ============================================
function verDetalle(ordenId) {
    // Redirigir a la página de detalle
    window.location.href = `detalle.html?id=${ordenId}`;
}

// ============================================
// Auto-refresh (opcional)
// ============================================
function iniciarAutoRefresh(intervaloSegundos = 30) {
    setInterval(() => {
        const estadoActual = document.getElementById('estado-filter').value;
        console.log('🔄 Auto-refresh...');
        cargarKPIs();
        cargarOrdenes(estadoActual);
    }, intervaloSegundos * 1000);
}

// Descomentar para activar auto-refresh cada 30 segundos
// iniciarAutoRefresh(30);