"""
Sistema de Tareas Programadas de Labortrovilo
Orquesta el flujo completo: Scraping → Procesamiento AI → Alertas → Notificaciones
"""
import logging
from datetime import datetime
from typing import Dict, Optional
import os
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from sqlalchemy.orm import Session

from database import SessionLocal
from notifications import AlertManager
from notification_channels import NotificationDispatcher
from models import Notification, User, AlertConfig, Job

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rutas de scripts
SCRIPTS_DIR = Path(__file__).parent.parent
SCRAPER_SCRIPT = SCRIPTS_DIR / "engine.py"
AI_PROCESSOR_SCRIPT = SCRIPTS_DIR / "test_ai_processor.py"


class TaskOrchestrator:
    """
    Orquestador central de tareas programadas
    Coordina el flujo completo del sistema
    """
    
    def __init__(self):
        self.scheduler = None
        self.alert_manager = AlertManager()
        self.notification_dispatcher = NotificationDispatcher()
        
        # Configuración de APScheduler
        self.executors = {
            'default': ThreadPoolExecutor(max_workers=5),
            'processpool': ProcessPoolExecutor(max_workers=2)
        }
        
        self.job_defaults = {
            'coalesce': True,  # Combinar ejecuciones perdidas
            'max_instances': 1,  # Solo una instancia de cada job
            'misfire_grace_time': 300  # 5 minutos de gracia
        }
    
    def start(self):
        """
        Inicia el scheduler y registra todas las tareas
        """
        if self.scheduler is not None:
            logger.warning("Scheduler ya está en ejecución")
            return
        
        self.scheduler = BackgroundScheduler(
            executors=self.executors,
            job_defaults=self.job_defaults,
            timezone='America/Mexico_City'  # Ajustar según zona horaria
        )
        
        # Registrar tareas
        self._register_jobs()
        
        # Iniciar scheduler
        self.scheduler.start()
        logger.info("TaskOrchestrator iniciado exitosamente")
        
        # Imprimir trabajos programados
        self._print_scheduled_jobs()
    
    def _register_jobs(self):
        """
        Registra todos los trabajos programados
        """
        # 1. Scraping cada 6 horas
        self.scheduler.add_job(
            func=self.run_scraper_job,
            trigger=IntervalTrigger(hours=6),
            id='scraper_job',
            name='Web Scraping Job',
            replace_existing=True
        )
        logger.info("✓ Scraper job registrado (cada 6 horas)")
        
        # 2. Procesamiento AI cada 6 horas (15 minutos después del scraping)
        self.scheduler.add_job(
            func=self.run_ai_processor_job,
            trigger=CronTrigger(hour='*/6', minute='15'),
            id='ai_processor_job',
            name='AI Processing Job',
            replace_existing=True
        )
        logger.info("✓ AI Processor job registrado (cada 6h + 15min)")
        
        # 3. Revisión de alertas cada hora
        self.scheduler.add_job(
            func=self.run_alert_check_job,
            trigger=IntervalTrigger(hours=1),
            id='alert_check_job',
            name='Alert Check Job',
            replace_existing=True
        )
        logger.info("✓ Alert Check job registrado (cada hora)")
        
        # 4. Envío de notificaciones pendientes cada 15 minutos
        self.scheduler.add_job(
            func=self.send_pending_notifications_job,
            trigger=IntervalTrigger(minutes=15),
            id='send_notifications_job',
            name='Send Notifications Job',
            replace_existing=True
        )
        logger.info("✓ Send Notifications job registrado (cada 15 minutos)")
        
        # 5. Limpieza de notificaciones antiguas (diario a las 3 AM)
        self.scheduler.add_job(
            func=self.cleanup_old_notifications_job,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_job',
            name='Cleanup Old Notifications',
            replace_existing=True
        )
        logger.info("✓ Cleanup job registrado (diario 3:00 AM)")
        
        # 6. Reporte diario de estadísticas (diario a las 9 AM)
        self.scheduler.add_job(
            func=self.daily_stats_report_job,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_stats_job',
            name='Daily Stats Report',
            replace_existing=True
        )
        logger.info("✓ Daily Stats job registrado (diario 9:00 AM)")
    
    def run_scraper_job(self):
        """
        Ejecuta el scraper de ofertas de empleo
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: Web Scraping Job")
        logger.info("=" * 60)
        
        try:
            import subprocess
            
            # Ejecutar scraper usando Python
            result = subprocess.run(
                ['python', str(SCRAPER_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora máximo
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Scraper ejecutado exitosamente")
                logger.info(f"Output: {result.stdout[:500]}")
                return True
            else:
                logger.error(f"✗ Error en scraper: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("✗ Scraper timeout (excedió 1 hora)")
            return False
        except Exception as e:
            logger.error(f"✗ Error ejecutando scraper: {str(e)}", exc_info=True)
            return False
    
    def run_ai_processor_job(self):
        """
        Ejecuta el procesador de AI para análisis de ofertas
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: AI Processing Job")
        logger.info("=" * 60)
        
        try:
            import subprocess
            
            # Ejecutar AI processor
            result = subprocess.run(
                ['python', str(AI_PROCESSOR_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos máximo
            )
            
            if result.returncode == 0:
                logger.info(f"✓ AI Processor ejecutado exitosamente")
                logger.info(f"Output: {result.stdout[:500]}")
                return True
            else:
                logger.error(f"✗ Error en AI Processor: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("✗ AI Processor timeout (excedió 30 minutos)")
            return False
        except Exception as e:
            logger.error(f"✗ Error ejecutando AI Processor: {str(e)}", exc_info=True)
            return False
    
    def run_alert_check_job(self):
        """
        Revisa nuevas ofertas y genera alertas según configuraciones de usuarios
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: Alert Check Job")
        logger.info("=" * 60)
        
        try:
            # Ejecutar revisión de alertas
            stats = self.alert_manager.check_new_jobs_for_alerts(hours_lookback=1)
            
            logger.info("Resultados de Alert Check:")
            logger.info(f"  - Jobs revisados: {stats['jobs_checked']}")
            logger.info(f"  - Alertas candidatos: {stats['candidate_alerts']}")
            logger.info(f"  - Alertas HR: {stats['hr_alerts']}")
            logger.info(f"  - Market signals: {stats['market_signals']}")
            logger.info(f"  - Golden Leads: {stats['golden_leads']}")
            logger.info(f"  - Total notificaciones: {stats['total_notifications']}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error en Alert Check: {str(e)}", exc_info=True)
            return False
    
    def send_pending_notifications_job(self):
        """
        Envía todas las notificaciones pendientes
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: Send Notifications Job")
        logger.info("=" * 60)
        
        db = SessionLocal()
        sent_count = 0
        failed_count = 0
        
        try:
            # Obtener notificaciones pendientes
            pending_notifications = (
                db.query(Notification)
                .filter(
                    Notification.is_sent == False,
                    Notification.sent_at.is_(None)
                )
                .order_by(Notification.urgency_score.desc())
                .limit(100)  # Procesar máximo 100 por ejecución
                .all()
            )
            
            logger.info(f"Notificaciones pendientes: {len(pending_notifications)}")
            
            for notification in pending_notifications:
                try:
                    # Obtener usuario
                    user = db.query(User).filter(User.id == notification.user_id).first()
                    if not user or not user.is_active:
                        logger.warning(f"Usuario {notification.user_id} no existe o inactivo")
                        continue
                    
                    # Obtener job si aplica
                    job = None
                    if notification.job_id:
                        job = db.query(Job).filter(Job.id == notification.job_id).first()
                    
                    # Obtener configuración de alertas
                    config = (
                        db.query(AlertConfig)
                        .filter(AlertConfig.user_id == user.id, AlertConfig.is_active == True)
                        .first()
                    )
                    
                    # Despachar notificación
                    success = self.notification_dispatcher.dispatch_notification(
                        notification=notification,
                        user=user,
                        job=job,
                        config=config
                    )
                    
                    if success:
                        # Marcar como enviada
                        notification.is_sent = True
                        notification.sent_at = datetime.utcnow()
                        db.commit()
                        sent_count += 1
                        logger.info(f"✓ Notificación {notification.id} enviada a {user.email}")
                    else:
                        failed_count += 1
                        logger.warning(f"✗ Falló envío de notificación {notification.id}")
                        
                except Exception as e:
                    logger.error(f"Error procesando notificación {notification.id}: {str(e)}")
                    failed_count += 1
                    continue
            
            logger.info(f"Resumen de envío: {sent_count} exitosas, {failed_count} fallidas")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error en Send Notifications Job: {str(e)}", exc_info=True)
            return False
        finally:
            db.close()
    
    def cleanup_old_notifications_job(self):
        """
        Limpia notificaciones antiguas (más de 30 días)
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: Cleanup Job")
        logger.info("=" * 60)
        
        db = SessionLocal()
        
        try:
            from datetime import timedelta
            
            # Eliminar notificaciones enviadas hace más de 30 días
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted_count = (
                db.query(Notification)
                .filter(
                    Notification.is_sent == True,
                    Notification.sent_at < cutoff_date
                )
                .delete()
            )
            
            db.commit()
            logger.info(f"✓ Limpiadas {deleted_count} notificaciones antiguas")
            return True
            
        except Exception as e:
            logger.error(f"✗ Error en Cleanup Job: {str(e)}", exc_info=True)
            db.rollback()
            return False
        finally:
            db.close()
    
    def daily_stats_report_job(self):
        """
        Genera reporte diario de estadísticas del sistema
        """
        logger.info("=" * 60)
        logger.info("INICIANDO: Daily Stats Report")
        logger.info("=" * 60)
        
        db = SessionLocal()
        
        try:
            from datetime import timedelta
            
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Estadísticas de notificaciones
            total_sent = (
                db.query(Notification)
                .filter(
                    Notification.is_sent == True,
                    Notification.sent_at >= yesterday
                )
                .count()
            )
            
            golden_leads = (
                db.query(Notification)
                .filter(
                    Notification.is_golden_lead == True,
                    Notification.created_at >= yesterday
                )
                .count()
            )
            
            # Estadísticas de jobs
            new_jobs = (
                db.query(Job)
                .filter(Job.scraped_date >= yesterday)
                .count()
            )
            
            # Usuarios activos
            active_users = (
                db.query(User)
                .filter(User.is_active == True)
                .count()
            )
            
            logger.info("📊 REPORTE DIARIO DE ESTADÍSTICAS")
            logger.info(f"  - Nuevas ofertas scrapeadas: {new_jobs}")
            logger.info(f"  - Notificaciones enviadas: {total_sent}")
            logger.info(f"  - Golden Leads detectados: {golden_leads}")
            logger.info(f"  - Usuarios activos: {active_users}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error generando reporte: {str(e)}", exc_info=True)
            return False
        finally:
            db.close()
    
    def _print_scheduled_jobs(self):
        """
        Imprime información sobre los trabajos programados
        """
        logger.info("")
        logger.info("=" * 60)
        logger.info("TRABAJOS PROGRAMADOS")
        logger.info("=" * 60)
        
        for job in self.scheduler.get_jobs():
            logger.info(f"  • {job.name}")
            logger.info(f"    ID: {job.id}")
            logger.info(f"    Trigger: {job.trigger}")
            logger.info(f"    Próxima ejecución: {job.next_run_time}")
            logger.info("")
    
    def stop(self):
        """
        Detiene el scheduler
        """
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("TaskOrchestrator detenido")
    
    def pause_job(self, job_id: str):
        """
        Pausa un trabajo específico
        """
        if self.scheduler:
            self.scheduler.pause_job(job_id)
            logger.info(f"Trabajo {job_id} pausado")
    
    def resume_job(self, job_id: str):
        """
        Reanuda un trabajo pausado
        """
        if self.scheduler:
            self.scheduler.resume_job(job_id)
            logger.info(f"Trabajo {job_id} reanudado")
    
    def trigger_job_now(self, job_id: str):
        """
        Ejecuta un trabajo inmediatamente
        """
        if self.scheduler:
            job = self.scheduler.get_job(job_id)
            if job:
                job.func()
                logger.info(f"Trabajo {job_id} ejecutado manualmente")
            else:
                logger.error(f"Trabajo {job_id} no encontrado")


# Instancia global del orquestador
_orchestrator: Optional[TaskOrchestrator] = None


def get_orchestrator() -> TaskOrchestrator:
    """
    Obtiene la instancia global del orquestador (Singleton)
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TaskOrchestrator()
    return _orchestrator


def start_scheduler():
    """
    Inicia el sistema de tareas programadas
    """
    orchestrator = get_orchestrator()
    orchestrator.start()
    return orchestrator


def stop_scheduler():
    """
    Detiene el sistema de tareas programadas
    """
    global _orchestrator
    if _orchestrator:
        _orchestrator.stop()
        _orchestrator = None


if __name__ == "__main__":
    # Modo CLI
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "start":
            print("🚀 Iniciando Task Orchestrator...")
            orchestrator = start_scheduler()
            
            try:
                # Mantener el proceso vivo
                import time
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n⏹️  Deteniendo Task Orchestrator...")
                stop_scheduler()
                print("✓ Detenido exitosamente")
        
        elif command == "test":
            print("🧪 Ejecutando test de trabajos...")
            orchestrator = get_orchestrator()
            orchestrator.start()
            
            # Ejecutar manualmente cada trabajo
            print("\n1. Testing Scraper Job...")
            orchestrator.run_scraper_job()
            
            print("\n2. Testing Alert Check Job...")
            orchestrator.run_alert_check_job()
            
            print("\n3. Testing Send Notifications Job...")
            orchestrator.send_pending_notifications_job()
            
            print("\n4. Testing Daily Stats Job...")
            orchestrator.daily_stats_report_job()
            
            orchestrator.stop()
            print("\n✓ Tests completados")
        
        else:
            print(f"Comando desconocido: {command}")
            print("Uso: python scheduler.py [start|test]")
    else:
        print("Uso: python scheduler.py [start|test]")
        print("  start - Inicia el scheduler en background")
        print("  test  - Ejecuta todos los trabajos una vez para testing")
