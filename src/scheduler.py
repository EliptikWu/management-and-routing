"""
Configuración de APScheduler para el temporizador
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import atexit

from src.database import SessionLocal
from src.services.temporizador_service import TemporizadorService
from src.config import settings


class TemporizadorScheduler:
    """Singleton para manejar el scheduler del temporizador"""
    
    _instance = None
    _scheduler = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemporizadorScheduler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._scheduler is None:
            self._scheduler = BackgroundScheduler(
                timezone='UTC',
                daemon=True
            )
            self._configurar_jobs()
    
    def _configurar_jobs(self):
        """Configura los jobs del scheduler"""
        # Job principal: ejecutar tick cada N_SEG segundos
        self._scheduler.add_job(
            func=self._ejecutar_tick_job,
            trigger=IntervalTrigger(seconds=settings.N_SEG),
            id='temporizador_tick',
            name='Temporizador - Incrementar segundos y aplicar SLA',
            replace_existing=True,
            max_instances=1  # Evitar ejecuciones concurrentes
        )
        
        print(f"✅ Scheduler configurado: tick cada {settings.N_SEG}s, SLA={settings.SLA_SEG}s")
    
    def _ejecutar_tick_job(self):
        """Wrapper para ejecutar el tick con manejo de sesión"""
        db = SessionLocal()
        try:
            TemporizadorService.ejecutar_tick(db)
        except Exception as e:
            print(f"❌ Error en job de temporizador: {e}")
        finally:
            db.close()
    
    def iniciar(self):
        """Inicia el scheduler"""
        if not self._scheduler.running:
            self._scheduler.start()
            print(f"🚀 Temporizador iniciado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Registrar shutdown automático
            atexit.register(self.detener)
    
    def detener(self):
        """Detiene el scheduler"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=True)
            print("⏹️  Temporizador detenido")
    
    def obtener_jobs(self):
        """Retorna información sobre los jobs activos"""
        if not self._scheduler:
            return []
        
        jobs_info = []
        for job in self._scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs_info
    
    def ejecutar_tick_manual(self):
        """Ejecuta un tick manualmente (útil para testing)"""
        print("🔧 Ejecutando tick manual...")
        self._ejecutar_tick_job()


# Instancia global del scheduler
temporizador_scheduler = TemporizadorScheduler()