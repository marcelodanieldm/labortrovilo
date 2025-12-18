"""
Sistema de Notificaciones de Labortrovilo - AlertManager
Gestiona alertas inteligentes para candidatos y HR professionals
Incluye el concepto de "The Golden Lead" para oportunidades excepcionales
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from models import Job, Company, User, AlertConfig, Notification, UserRole, NotificationChannel
from database import get_db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertManager:
    """
    Gestor central de alertas del sistema
    Procesa reglas de alertas y genera notificaciones
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def check_new_jobs_for_alerts(self, hours_lookback: int = 1) -> Dict[str, int]:
        """
        Revisa ofertas nuevas y genera alertas según configuraciones de usuarios
        
        Args:
            hours_lookback: Cuántas horas atrás revisar ofertas
            
        Returns:
            Dict con estadísticas de alertas generadas
        """
        logger.info(f"Revisando ofertas de las últimas {hours_lookback} horas...")
        
        # Obtener ofertas nuevas
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_lookback)
        new_jobs = self.db.query(Job).filter(
            Job.scraped_at >= cutoff_time
        ).all()
        
        logger.info(f"Encontradas {len(new_jobs)} ofertas nuevas")
        
        stats = {
            'total_jobs': len(new_jobs),
            'candidate_alerts': 0,
            'hr_alerts': 0,
            'golden_leads': 0,
            'notifications_created': 0
        }
        
        # Procesar alertas para cada tipo de usuario
        stats['candidate_alerts'] = self._process_candidate_alerts(new_jobs)
        stats['hr_alerts'] = self._process_hr_alerts(new_jobs)
        stats['golden_leads'] = self._identify_golden_leads(new_jobs)
        
        # Procesar market signals
        stats['market_signals'] = self._process_market_signals()
        
        self.db.commit()
        logger.info(f"Alertas generadas: {stats}")
        
        return stats
    
    def _process_candidate_alerts(self, jobs: List[Job]) -> int:
        """
        Procesa alertas para candidatos basadas en tech stack y salario
        
        Returns:
            Número de alertas generadas
        """
        alerts_generated = 0
        
        # Obtener configuraciones activas de candidatos
        candidate_configs = self.db.query(AlertConfig).join(User).filter(
            and_(
                AlertConfig.is_active == True,
                User.role == UserRole.CANDIDATO,
                User.is_active == True
            )
        ).all()
        
        logger.info(f"Procesando {len(candidate_configs)} configuraciones de candidatos")
        
        for config in candidate_configs:
            for job in jobs:
                if self._job_matches_candidate_criteria(job, config):
                    # Verificar si ya existe notificación para este job/usuario
                    existing = self.db.query(Notification).filter(
                        and_(
                            Notification.user_id == config.user_id,
                            Notification.job_id == job.id
                        )
                    ).first()
                    
                    if not existing:
                        # Crear notificación
                        self._create_job_notification(
                            user_id=config.user_id,
                            job=job,
                            config=config,
                            notification_type="JOB_MATCH"
                        )
                        alerts_generated += 1
        
        return alerts_generated
    
    def _process_hr_alerts(self, jobs: List[Job]) -> int:
        """
        Procesa alertas para HR professionals
        
        Returns:
            Número de alertas generadas
        """
        alerts_generated = 0
        
        # Obtener configuraciones activas de HR
        hr_configs = self.db.query(AlertConfig).join(User).filter(
            and_(
                AlertConfig.is_active == True,
                User.role == UserRole.HR_PRO,
                User.is_active == True
            )
        ).all()
        
        logger.info(f"Procesando {len(hr_configs)} configuraciones de HR")
        
        for config in hr_configs:
            for job in jobs:
                if self._job_matches_hr_criteria(job, config):
                    existing = self.db.query(Notification).filter(
                        and_(
                            Notification.user_id == config.user_id,
                            Notification.job_id == job.id
                        )
                    ).first()
                    
                    if not existing:
                        self._create_job_notification(
                            user_id=config.user_id,
                            job=job,
                            config=config,
                            notification_type="HR_MATCH"
                        )
                        alerts_generated += 1
        
        return alerts_generated
    
    def _process_market_signals(self) -> int:
        """
        Detecta señales de mercado importantes para HR
        Ejemplo: Empresa publicando muchos puestos en poco tiempo
        
        Returns:
            Número de señales detectadas
        """
        signals_detected = 0
        
        # Buscar empresas con alta velocidad de contratación (últimas 24 horas)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        hiring_velocity = self.db.query(
            Job.company_name,
            func.count(Job.id).label('job_count')
        ).filter(
            Job.scraped_at >= cutoff_time
        ).group_by(
            Job.company_name
        ).having(
            func.count(Job.id) >= 3  # Al menos 3 puestos en un día
        ).all()
        
        if not hiring_velocity:
            return 0
        
        logger.info(f"Detectadas {len(hiring_velocity)} empresas con alta velocidad de contratación")
        
        # Notificar a HR professionals con market signals habilitados
        hr_users = self.db.query(User).join(AlertConfig).filter(
            and_(
                User.role == UserRole.HR_PRO,
                User.is_active == True,
                AlertConfig.is_active == True,
                AlertConfig.enable_market_signals == True
            )
        ).distinct().all()
        
        for company_name, job_count in hiring_velocity:
            for user in hr_users:
                # Verificar si ya notificamos esta señal hoy
                today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                existing = self.db.query(Notification).filter(
                    and_(
                        Notification.user_id == user.id,
                        Notification.notification_type == "MARKET_SIGNAL",
                        Notification.created_at >= today,
                        Notification.extra_data['company_name'].astext == company_name
                    )
                ).first()
                
                if not existing:
                    notification = Notification(
                        user_id=user.id,
                        notification_type="MARKET_SIGNAL",
                        title=f"🚀 Market Signal: {company_name}",
                        message=f"{company_name} ha publicado {job_count} puestos en las últimas 24 horas. Alta velocidad de contratación detectada.",
                        channel=NotificationChannel.EMAIL,  # Default, se enviará por canales configurados
                        extra_data={
                            'company_name': company_name,
                            'job_count': job_count,
                            'signal_type': 'HIGH_HIRING_VELOCITY'
                        }
                    )
                    self.db.add(notification)
                    signals_detected += 1
        
        return signals_detected
    
    def _identify_golden_leads(self, jobs: List[Job]) -> int:
        """
        Identifica "Golden Leads" - oportunidades excepcionales
        Criterios: hiring_urgency_score > 0.9 y growth_score alto
        
        Returns:
            Número de Golden Leads identificados
        """
        golden_leads = 0
        
        for job in jobs:
            # Calcular scores (simplificado - en producción usar AI processor)
            urgency_score = self._calculate_urgency_score(job)
            
            # Si hay empresa asociada, obtener growth_score
            growth_score = 0
            if job.company:
                growth_score = job.company.growth_score or 0
            
            # Criterios para Golden Lead
            is_golden = (
                urgency_score > 0.9 and 
                growth_score > 0.7 and
                job.salary_max and job.salary_max > 100000  # Salario alto
            )
            
            if is_golden:
                logger.info(f"🌟 Golden Lead detectado: {job.title} en {job.company_name}")
                
                # Notificar a todos los usuarios con configuraciones que coincidan
                self._create_golden_lead_notifications(job, urgency_score)
                golden_leads += 1
        
        return golden_leads
    
    def _job_matches_candidate_criteria(self, job: Job, config: AlertConfig) -> bool:
        """
        Verifica si un trabajo cumple los criterios de un candidato
        
        Args:
            job: Oferta de trabajo
            config: Configuración de alerta del candidato
            
        Returns:
            True si el trabajo coincide con los criterios
        """
        # Tech Stack
        if config.tech_stack:
            job_stack = job.cleaned_stack or ""
            job_stack_lower = job_stack.lower()
            
            # Verificar si alguna tecnología del filtro está en el stack del job
            tech_match = any(
                tech.lower() in job_stack_lower 
                for tech in config.tech_stack
            )
            
            if not tech_match:
                return False
        
        # Rango salarial
        if config.salary_min and job.salary_max:
            if job.salary_max < config.salary_min:
                return False
        
        if config.salary_max and job.salary_min:
            if job.salary_min > config.salary_max:
                return False
        
        # Keywords en título o descripción
        if config.keywords:
            text_to_search = f"{job.title} {job.raw_description or ''}".lower()
            keyword_match = any(
                keyword.lower() in text_to_search
                for keyword in config.keywords
            )
            
            if not keyword_match:
                return False
        
        # Modalidad
        if config.modality:
            job_description = (job.raw_description or "").lower()
            if config.modality.lower() not in job_description:
                return False
        
        return True
    
    def _job_matches_hr_criteria(self, job: Job, config: AlertConfig) -> bool:
        """
        Verifica si un trabajo es relevante para un HR professional
        Similar a candidatos pero con enfoque diferente
        """
        # HR puede estar interesado en tecnologías específicas para reclutamiento
        if config.tech_stack:
            job_stack = job.cleaned_stack or ""
            job_stack_lower = job_stack.lower()
            
            tech_match = any(
                tech.lower() in job_stack_lower 
                for tech in config.tech_stack
            )
            
            if not tech_match:
                return False
        
        # Keywords relevantes
        if config.keywords:
            text_to_search = f"{job.title} {job.raw_description or ''}".lower()
            keyword_match = any(
                keyword.lower() in text_to_search
                for keyword in config.keywords
            )
            
            if not keyword_match:
                return False
        
        return True
    
    def _calculate_urgency_score(self, job: Job) -> float:
        """
        Calcula un score de urgencia para una oferta
        Basado en varios factores
        
        Returns:
            Score entre 0 y 1
        """
        score = 0.5  # Base score
        
        # Factor 1: Recencia (cuanto más reciente, más urgente)
        if job.posted_date:
            days_old = (datetime.utcnow() - job.posted_date).days
            if days_old < 1:
                score += 0.2
            elif days_old < 3:
                score += 0.1
        
        # Factor 2: Palabras clave de urgencia en descripción
        urgency_keywords = ['urgente', 'inmediato', 'asap', 'immediate', 'urgent']
        description = (job.raw_description or "").lower()
        if any(keyword in description for keyword in urgency_keywords):
            score += 0.2
        
        # Factor 3: Salario alto (indica posición importante)
        if job.salary_max and job.salary_max > 150000:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _create_job_notification(
        self, 
        user_id: int, 
        job: Job, 
        config: AlertConfig,
        notification_type: str
    ):
        """
        Crea una notificación para un usuario sobre un trabajo
        """
        # Construir mensaje personalizado
        title = f"Nueva oportunidad: {job.title}"
        
        salary_info = ""
        if job.salary_min or job.salary_max:
            if job.salary_min and job.salary_max:
                salary_info = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
            elif job.salary_max:
                salary_info = f"Hasta ${job.salary_max:,.0f}"
            elif job.salary_min:
                salary_info = f"Desde ${job.salary_min:,.0f}"
        
        tech_stack = job.cleaned_stack or "No especificado"
        
        message = f"""
        Empresa: {job.company_name}
        Tech Stack: {tech_stack}
        Salario: {salary_info if salary_info else 'No especificado'}
        URL: {job.source_url}
        """
        
        # Crear notificación para cada canal configurado
        for channel in config.channels:
            notification = Notification(
                user_id=user_id,
                job_id=job.id,
                notification_type=notification_type,
                title=title,
                message=message.strip(),
                channel=NotificationChannel[channel],
                extra_data={
                    'config_name': config.name,
                    'tech_stack': tech_stack,
                    'salary_range': salary_info
                }
            )
            self.db.add(notification)
    
    def _create_golden_lead_notifications(self, job: Job, urgency_score: float):
        """
        Crea notificaciones especiales para Golden Leads
        Se envía a usuarios cuyas configuraciones coincidan
        """
        # Obtener todos los usuarios activos que podrían estar interesados
        active_users = self.db.query(User).join(AlertConfig).filter(
            and_(
                User.is_active == True,
                AlertConfig.is_active == True
            )
        ).distinct().all()
        
        for user in active_users:
            # Verificar si alguna configuración del usuario coincide
            matching_configs = [
                config for config in user.alert_configs
                if config.is_active and self._job_matches_candidate_criteria(job, config)
            ]
            
            if matching_configs:
                config = matching_configs[0]  # Usar la primera configuración que coincida
                
                title = f"🌟 GOLDEN LEAD: {job.title}"
                message = f"""
                ⚡ OPORTUNIDAD ÚNICA ⚡
                
                Empresa: {job.company_name}
                Tech Stack: {job.cleaned_stack or 'No especificado'}
                Salario: ${job.salary_max:,.0f} (Top tier)
                Urgency Score: {urgency_score:.2f}/1.0
                Growth Score: {job.company.growth_score if job.company else 'N/A'}
                
                Esta oferta cumple con criterios excepcionales:
                • Alta urgencia de contratación
                • Empresa en crecimiento
                • Compensación competitiva
                
                URL: {job.source_url}
                """
                
                # Crear notificación marcada como Golden Lead
                for channel in config.channels:
                    notification = Notification(
                        user_id=user.id,
                        job_id=job.id,
                        notification_type="GOLDEN_LEAD",
                        title=title,
                        message=message.strip(),
                        channel=NotificationChannel[channel],
                        is_golden_lead=True,
                        urgency_score=urgency_score,
                        extra_data={
                            'config_name': config.name,
                            'is_priority': True
                        }
                    )
                    self.db.add(notification)
    
    def get_pending_notifications(self, channel: Optional[NotificationChannel] = None) -> List[Notification]:
        """
        Obtiene notificaciones pendientes de envío
        
        Args:
            channel: Filtrar por canal específico (opcional)
            
        Returns:
            Lista de notificaciones pendientes
        """
        query = self.db.query(Notification).filter(
            Notification.is_sent == False
        )
        
        if channel:
            query = query.filter(Notification.channel == channel)
        
        return query.all()
    
    def mark_notification_as_sent(self, notification_id: int):
        """
        Marca una notificación como enviada
        """
        notification = self.db.query(Notification).get(notification_id)
        if notification:
            notification.is_sent = True
            notification.sent_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Notificación {notification_id} marcada como enviada")


def run_alert_check(hours_lookback: int = 1):
    """
    Función principal para ejecutar la revisión de alertas
    Puede ser llamada por el scheduler
    """
    logger.info("=" * 50)
    logger.info("Iniciando revisión de alertas...")
    logger.info("=" * 50)
    
    db = next(get_db())
    try:
        alert_manager = AlertManager(db)
        stats = alert_manager.check_new_jobs_for_alerts(hours_lookback)
        
        logger.info("Revisión de alertas completada")
        logger.info(f"Estadísticas: {stats}")
        
        return stats
    except Exception as e:
        logger.error(f"Error en revisión de alertas: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Ejecutar revisión de alertas (para testing)
    run_alert_check(hours_lookback=24)
