/**
 * ============================================
 * Detalle de Orden - JavaScript
 * ============================================
 */

// Configuración
const API_BASE_URL = 'http://localhost:8000';
let ordenId = null;
let ordenData = null;
let modalCallback = null;

// Mapeo de estados a acciones permitidas
const ACCIONES_POR_ESTADO = {
    'ASIGNADA': ['iniciar', 'cerrar'],
    'EN_PROGRESO': ['pausar', 'completar', 'cerrar'],
    'PENDIENTE': ['iniciar', 'completar', 'cerrar'],
    'COMPLETADA': [],
    'CERRADA_SIN_SOLUCION': [],
    'VENCIDA': ['iniciar', 'completar', 'cerrar']
};

// Mapeo de acciones a nuevos estados
const ESTADO_POR_ACCION = {
    'iniciar': 'EN_PROGRESO',
    'pausar': 'PENDIENTE',
    'completar': 'COMPLETADA',
    'cerrar': 'CERRADA_SIN_SOLUCION'
};

// ============================================
// Inicialización
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    obtenerOrdenIdDeURL();
    
    if (ordenId) {
        initializeApp();
        setupEventListeners();
    } else {
        mostrarError('No se especificó un ID de orden válido');
    }
});

function obtenerOrdenIdDeURL() {
    const params = new URLSearchParams(window.location.search);
    ordenId = parseInt(params.get('id'));
}

function initializeApp() {
    console.log(`🚀 Cargando orden #${ordenId}...`);
    cargarOrden();
    cargarHistorial();
}

function setupEventListeners() {
    // Botón de actualizar
    const btnRefresh = document.getElementById('btn-refresh-detalle');
    btnRefresh.addEventListener('click', () => {
        cargarOrden();
        cargarHistorial();
    });
}

// ============================================
// Carga de Datos
// ============================================
async function cargarOrden() {
    mostrarLoading(true);
    ocultarMensajes();

    try {
        const response = await fetch(`${API_BASE_URL}/ordenes/${ordenId}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Orden no encontrada');
            }
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        ordenData = await response.json();
        renderizarOrden(ordenData);
        
    } catch (error) {
        console.error('❌ Error al cargar orden:', error);
        mostrarError(`No se pudo cargar la orden: ${error.message}`);
    } finally {
        mostrarLoading(false);
    }
}

async function cargarHistorial() {
    try {
        const response = await fetch(`${API_BASE_URL}/ordenes/${ordenId}/historial`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}`);
        }

        const historial = await response.json();
        renderizarHistorial(historial);
        
    } catch (error) {
        console.error('❌ Error al cargar historial:', error);
        // No mostramos error aquí para no saturar al usuario
    }
}

// ============================================
// Renderizado de Orden
// ============================================
function renderizarOrden(orden) {
    // Header
    document.getElementById('orden-titulo').textContent = orden.titulo;
    document.getElementById('orden-id').textContent = `#${orden.id}`;
    document.getElementById('orden-creador').textContent = orden.creador;

    // Info general
    document.getElementById('estado-global-badge').innerHTML = renderEstadoBadge(orden.estado_global);
    document.getElementById('prioridad-badge').innerHTML = renderPrioridadBadge(orden.prioridad);
    document.getElementById('fecha-creacion').textContent = formatearFechaCompleta(orden.creada_en);
    document.getElementById('fecha-actualizacion').textContent = formatearFechaRelativa(orden.actualizada_en);
    document.getElementById('orden-descripcion').textContent = orden.descripcion;

    // Áreas asignadas
    renderizarAreas(orden.asignaciones);
}

function renderizarAreas(asignaciones) {
    const container = document.getElementById('areas-container');
    const emptyState = document.getElementById('areas-empty');
    const countBadge = document.getElementById('areas-count');

    countBadge.textContent = `${asignaciones.length} ${asignaciones.length === 1 ? 'área' : 'áreas'}`;

    if (asignaciones.length === 0) {
        container.innerHTML = '';
        emptyState.hidden = false;
        return;
    }

    emptyState.hidden = true;
    container.innerHTML = '';

    asignaciones.forEach(asignacion => {
        const card = crearAreaCard(asignacion);
        container.appendChild(card);
    });
}

function crearAreaCard(asignacion) {
    const card = document.createElement('div');
    card.className = `area-card estado-${asignacion.estado_parcial.toLowerCase()}`;
    card.id = `area-${asignacion.area_id}`;

    const acciones = ACCIONES_POR_ESTADO[asignacion.estado_parcial] || [];
    const botonesHTML = generarBotonesAccion(asignacion.area_id, asignacion.estado_parcial, acciones);

    card.innerHTML = `
        <div class="area-header">
            <div>
                <h3 class="area-nombre">${escapeHtml(asignacion.area_nombre || 'Área sin nombre')}</h3>
                ${asignacion.asignada_a ? `<p class="area-asignada">${escapeHtml(asignacion.asignada_a)}</p>` : ''}
            </div>
            ${renderEstadoBadge(asignacion.estado_parcial)}
        </div>

        <div class="area-stats">
            <div class="stat-box">
                <span class="stat-label">Estado</span>
                <span class="stat-value">${traducirEstado(asignacion.estado_parcial)}</span>
            </div>
            <div class="stat-box">
                <span class="stat-label">Tiempo</span>
                <span class="stat-value">${formatearSegundos(asignacion.seg_acumulados)}</span>
            </div>
        </div>

        ${botonesHTML}
    `;

    return card;
}

function generarBotonesAccion(areaId, estadoActual, acciones) {
    if (acciones.length === 0) {
        return `
            <div class="area-actions">
                <button class="btn-action btn-secondary" disabled>
                    ${estadoActual === 'COMPLETADA' ? '✅ Completada' : '❌ Cerrada'}
                </button>
            </div>
        `;
    }

    const botones = acciones.map(accion => {
        const config = {
            'iniciar': { label: '▶️ Iniciar', class: 'btn-iniciar' },
            'pausar': { label: '⏸️ Pausar', class: 'btn-pausar' },
            'completar': { label: '✅ Completar', class: 'btn-completar' },
            'cerrar': { label: '❌ Cerrar Sin Solución', class: 'btn-cerrar' }
        }[accion];

        return `
            <button 
                class="btn-action ${config.class}" 
                onclick="confirmarAccion('${accion}', ${areaId}, '${estadoActual}')"
                aria-label="${config.label} área ${areaId}"
            >
                ${config.label}
            </button>
        `;
    }).join('');

    return `<div class="area-actions">${botones}</div>`;
}

// ============================================
// Renderizado de Historial
// ============================================
function renderizarHistorial(historial) {
    const container = document.getElementById('historial-container');
    const emptyState = document.getElementById('historial-empty');
    const countBadge = document.getElementById('historial-count');

    countBadge.textContent = `${historial.length} ${historial.length === 1 ? 'evento' : 'eventos'}`;

    if (historial.length === 0) {
        container.innerHTML = '';
        emptyState.hidden = false;
        return;
    }

    emptyState.hidden = true;
    container.innerHTML = '';

    historial.forEach(evento => {
        const item = crearHistorialItem(evento);
        container.appendChild(item);
    });
}

function crearHistorialItem(evento) {
    const item = document.createElement('div');
    const eventoClass = evento.evento.toLowerCase().replace(/_/g, '_');
    item.className = `historial-item evento-${eventoClass}`;

    item.innerHTML = `
        <div class="historial-header">
            <span class="historial-evento">${formatearEvento(evento.evento)}</span>
            <span class="historial-timestamp">${formatearFechaRelativa(evento.timestamp)}</span>
        </div>
        ${evento.detalle ? `<p class="historial-detalle">${escapeHtml(evento.detalle)}</p>` : ''}
        <div class="historial-footer">
            ${evento.actor ? `<span class="historial-actor">${escapeHtml(evento.actor)}</span>` : ''}
            ${evento.estado_global ? renderEstadoBadge(evento.estado_global, true) : ''}
        </div>
    `;

    return item;
}

// ============================================
// Acciones (Cambio de Estado)
// ============================================
function confirmarAccion(accion, areaId, estadoActual) {
    const mensajes = {
        'iniciar': '¿Deseas iniciar el trabajo en esta área?',
        'pausar': '¿Deseas pausar temporalmente esta área?',
        'completar': '¿Confirmas que esta área ha completado su trabajo?',
        'cerrar': '¿Deseas cerrar esta área sin solución? Esta acción indica que no se pudo resolver.'
    };

    const titulo = {
        'iniciar': 'Iniciar Trabajo',
        'pausar': 'Pausar Trabajo',
        'completar': 'Completar Área',
        'cerrar': 'Cerrar Sin Solución'
    };

    // Configurar modal
    document.getElementById('modal-title').textContent = titulo[accion];
    document.getElementById('modal-mensaje').textContent = mensajes[accion];
    
    // Mostrar campo de notas para completar y cerrar
    const notasGroup = document.getElementById('modal-notas-group');
    notasGroup.hidden = !['completar', 'cerrar'].includes(accion);
    document.getElementById('modal-notas').value = '';

    // Configurar callback de confirmación
    modalCallback = () => ejecutarAccion(accion, areaId);

    // Mostrar modal
    mostrarModal();
}

async function ejecutarAccion(accion, areaId) {
    const nuevoEstado = ESTADO_POR_ACCION[accion];
    const notas = document.getElementById('modal-notas').value.trim();

    cerrarModal();
    mostrarLoading(true);
    ocultarMensajes();

    try {
        const body = {
            nuevo_estado: nuevoEstado
        };

        if (notas) {
            body.notas = notas;
        }

        const response = await fetch(
            `${API_BASE_URL}/ordenes/${ordenId}/areas/${areaId}`,
            {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            }
        );

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `Error ${response.status}`);
        }

        const resultado = await response.json();
        
        // Actualizar UI optimistically
        actualizarAreaUI(areaId, resultado);
        
        // Recargar datos completos
        await Promise.all([
            cargarOrden(),
            cargarHistorial()
        ]);

        mostrarExito(`✅ Acción "${accion}" ejecutada correctamente`);

    } catch (error) {
        console.error('❌ Error al ejecutar acción:', error);
        mostrarError(`No se pudo ejecutar la acción: ${error.message}`);
        
        // Recargar para recuperar estado correcto
        cargarOrden();
    } finally {
        mostrarLoading(false);
    }
}

function actualizarAreaUI(areaId, datosActualizados) {
    const card = document.getElementById(`area-${areaId}`);
    if (!card) return;

    // Actualizar badge de estado
    const badge = card.querySelector('.estado-badge');
    if (badge) {
        badge.outerHTML = renderEstadoBadge(datosActualizados.estado_parcial);
    }

    // Actualizar clase del card
    card.className = `area-card estado-${datosActualizados.estado_parcial.toLowerCase()}`;

    // Actualizar segundos acumulados
    const statValue = card.querySelector('.stat-box:last-child .stat-value');
    if (statValue) {
        statValue.textContent = formatearSegundos(datosActualizados.seg_acumulados);
    }
}

// ============================================
// Modal
// ============================================
function mostrarModal() {
    const modal = document.getElementById('modal-confirmacion');
    modal.hidden = false;
    document.body.style.overflow = 'hidden';

    // Configurar botón de confirmar
    const btnConfirmar = document.getElementById('btn-modal-confirmar');
    btnConfirmar.onclick = () => {
        if (modalCallback) {
            modalCallback();
        }
    };

    // Focus en el primer elemento
    setTimeout(() => {
        const textarea = document.getElementById('modal-notas');
        if (!textarea.parentElement.hidden) {
            textarea.focus();
        } else {
            btnConfirmar.focus();
        }
    }, 100);
}

function cerrarModal() {
    const modal = document.getElementById('modal-confirmacion');
    modal.hidden = true;
    document.body.style.overflow = '';
    modalCallback = null;
}

// Cerrar modal con Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const modal = document.getElementById('modal-confirmacion');
        if (!modal.hidden) {
            cerrarModal();
        }
    }
});

// ============================================
// Helpers de Renderizado
// ============================================
function renderEstadoBadge(estado, small = false) {
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
    const sizeClass = small ? 'estado-badge-small' : '';
    return `<span class="estado-badge estado-${config.class} ${sizeClass}">${config.label}</span>`;
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

function traducirEstado(estado) {
    const traducciones = {
        'NUEVA': 'Nueva',
        'ASIGNADA': 'Asignada',
        'EN_PROGRESO': 'Progreso',
        'PENDIENTE': 'Pausado',
        'COMPLETADA': 'Completada',
        'CERRADA_SIN_SOLUCION': 'Sin Solución',
        'VENCIDA': 'Vencida'
    };
    return traducciones[estado] || estado;
}

function formatearEvento(evento) {
    const eventos = {
        'CREADA': '🆕 Orden Creada',
        'AREA_ASIGNADA': '➕ Área Asignada',
        'AREA_REMOVIDA': '➖ Área Removida',
        'CAMBIO_ESTADO_PARCIAL': '🔄 Cambio de Estado (Área)',
        'CAMBIO_ESTADO_GLOBAL': '🌐 Cambio de Estado Global',
        'INICIO_TRABAJO': '▶️ Trabajo Iniciado',
        'COMPLETADA': '✅ Completada',
        'TIMEOUT_SLA': '⏰ SLA Superado',
        'CERRADA_SIN_SOLUCION': '❌ Cerrada Sin Solución'
    };
    return eventos[evento] || evento;
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

function formatearFechaRelativa(fechaISO) {
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

function formatearFechaCompleta(fechaISO) {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
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
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        errorDiv.hidden = true;
    }, 5000);
}

function mostrarExito(mensaje) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = mensaje;
    successDiv.hidden = false;
    
    // Auto-ocultar después de 3 segundos
    setTimeout(() => {
        successDiv.hidden = true;
    }, 3000);
}

function ocultarMensajes() {
    document.getElementById('error-message').hidden = true;
    document.getElementById('success-message').hidden = true;
}

// ============================================
// Navegación
// ============================================
function volverAtras() {
    window.location.href = 'index.html';
}