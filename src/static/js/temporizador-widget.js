/**
 * Widget de Temporizador (opcional)
 * Muestra información en tiempo real del temporizador
 */

class TemporizadorWidget {
    constructor() {
        this.intervalo = null;
        this.init();
    }

    init() {
        this.crearWidget();
        this.cargarEstado();
        this.iniciarActualizacion();
    }

    crearWidget() {
        // Crear contenedor del widget
        const widget = document.createElement('div');
        widget.id = 'temporizador-widget';
        widget.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            min-width: 200px;
            z-index: 999;
            font-size: 0.875rem;
        `;

        widget.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>⏱️ Temporizador</strong>
                <button id="widget-toggle" style="background: none; border: none; cursor: pointer; font-size: 1rem;">
                    ▼
                </button>
            </div>
            <div id="widget-content">
                <div style="margin-bottom: 8px;">
                    <span style="color: #6b7280;">Estado:</span>
                    <span id="widget-estado" style="font-weight: 600; margin-left: 4px;">--</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6b7280;">Intervalo:</span>
                    <span id="widget-intervalo" style="font-weight: 600; margin-left: 4px;">--</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6b7280;">SLA:</span>
                    <span id="widget-sla" style="font-weight: 600; margin-left: 4px;">--</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6b7280;">Áreas activas:</span>
                    <span id="widget-areas" style="font-weight: 600; margin-left: 4px;">--</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #6b7280;">Vencidas:</span>
                    <span id="widget-vencidas" style="font-weight: 600; margin-left: 4px; color: #dc2626;">--</span>
                </div>
                <button 
                    id="widget-tick-manual" 
                    style="
                        width: 100%;
                        padding: 8px;
                        background: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-weight: 600;
                        font-size: 0.75rem;
                        margin-top: 8px;
                    "
                >
                    🔄 Tick Manual
                </button>
            </div>
        `;

        document.body.appendChild(widget);

        // Event listeners
        document.getElementById('widget-toggle').addEventListener('click', () => {
            this.toggleWidget();
        });

        document.getElementById('widget-tick-manual').addEventListener('click', () => {
            this.ejecutarTickManual();
        });
    }

    async cargarEstado() {
        try {
            // Estado del temporizador
            const estadoResponse = await fetch('http://localhost:8000/temporizador/estado');
            const estado = await estadoResponse.json();

            document.getElementById('widget-estado').textContent = 
                estado.activo ? '🟢 Activo' : '🔴 Inactivo';
            document.getElementById('widget-intervalo').textContent = 
                `${estado.configuracion.n_seg}s`;
            document.getElementById('widget-sla').textContent = 
                `${estado.configuracion.sla_seg}s`;

            // Estadísticas de SLA
            const statsResponse = await fetch('http://localhost:8000/temporizador/estadisticas-sla');
            const stats = await statsResponse.json();

            document.getElementById('widget-areas').textContent = stats.total_areas_activas;
            document.getElementById('widget-vencidas').textContent = stats.areas_vencidas;

        } catch (error) {
            console.error('Error al cargar estado del temporizador:', error);
        }
    }

    async ejecutarTickManual() {
        const btn = document.getElementById('widget-tick-manual');
        btn.disabled = true;
        btn.textContent = '⏳ Ejecutando...';

        try {
            const response = await fetch('http://localhost:8000/temporizador/tick', {
                method: 'POST'
            });
            const resultado = await response.json();

            console.log('Tick manual ejecutado:', resultado);
            
            // Mostrar resultado brevemente
            btn.textContent = `✅ ${resultado.areas_actualizadas} actualizadas`;
            
            // Recargar estado
            setTimeout(() => {
                this.cargarEstado();
                btn.textContent = '🔄 Tick Manual';
                btn.disabled = false;
            }, 2000);

        } catch (error) {
            console.error('Error al ejecutar tick:', error);
            btn.textContent = '❌ Error';
            setTimeout(() => {
                btn.textContent = '🔄 Tick Manual';
                btn.disabled = false;
            }, 2000);
        }
    }

    iniciarActualizacion() {
        // Actualizar cada 5 segundos
        this.intervalo = setInterval(() => {
            this.cargarEstado();
        }, 5000);
    }

    toggleWidget() {
        const content = document.getElementById('widget-content');
        const toggle = document.getElementById('widget-toggle');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            toggle.textContent = '▼';
        } else {
            content.style.display = 'none';
            toggle.textContent = '▲';
        }
    }

    destruir() {
        if (this.intervalo) {
            clearInterval(this.intervalo);
        }
        const widget = document.getElementById('temporizador-widget');
        if (widget) {
            widget.remove();
        }
    }
}

// Auto-inicializar en páginas que lo necesiten
document.addEventListener('DOMContentLoaded', () => {
    // Solo en index.html y detalle.html
    if (window.location.pathname.includes('index.html') || 
        window.location.pathname.includes('detalle.html') ||
        window.location.pathname === '/app') {
        
        window.temporizadorWidget = new TemporizadorWidget();
    }
});