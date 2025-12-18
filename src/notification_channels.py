"""
Canales de Notificación de Labortrovilo
Implementa envío de notificaciones vía Email, Slack y Discord
"""
import logging
import os
from typing import Dict, Optional
from datetime import datetime
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from models import Notification, User, Job, NotificationChannel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@labortrovilo.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Labortrovilo")

# Configurar Jinja2 para plantillas de email
template_dir = Path(__file__).parent / "templates" / "email"
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailNotifier:
    """
    Gestor de notificaciones por email usando SendGrid
    """
    
    def __init__(self, api_key: str = SENDGRID_API_KEY):
        self.api_key = api_key
        self.from_email = SENDGRID_FROM_EMAIL
        self.from_name = SENDGRID_FROM_NAME
        
        if not self.api_key:
            logger.warning("SendGrid API key no configurada")
    
    def send_job_alert(
        self, 
        to_email: str, 
        user_name: str,
        job: Job,
        notification: Notification
    ) -> bool:
        """
        Envía una alerta de trabajo por email
        
        Args:
            to_email: Email del destinatario
            user_name: Nombre del usuario
            job: Oferta de trabajo
            notification: Objeto de notificación
            
        Returns:
            True si se envió exitosamente
        """
        try:
            # Renderizar plantilla HTML
            html_content = self._render_job_alert_template(
                user_name=user_name,
                job=job,
                notification=notification
            )
            
            # Construir asunto
            subject = notification.title
            if notification.is_golden_lead:
                subject = f"🌟 {subject}"
            
            # Enviar email
            return self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}", exc_info=True)
            return False
    
    def send_market_signal(
        self,
        to_email: str,
        user_name: str,
        notification: Notification
    ) -> bool:
        """
        Envía una señal de mercado por email
        """
        try:
            html_content = self._render_market_signal_template(
                user_name=user_name,
                notification=notification
            )
            
            return self._send_email(
                to_email=to_email,
                subject=notification.title,
                html_content=html_content
            )
            
        except Exception as e:
            logger.error(f"Error enviando market signal a {to_email}: {str(e)}", exc_info=True)
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Envía un email usando SendGrid
        """
        if not self.api_key:
            logger.warning(f"No se puede enviar email (API key no configurada): {to_email}")
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            logger.info(f"Email enviado a {to_email} - Status: {response.status_code}")
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error con SendGrid: {str(e)}", exc_info=True)
            return False
    
    def _render_job_alert_template(
        self, 
        user_name: str, 
        job: Job, 
        notification: Notification
    ) -> str:
        """
        Renderiza la plantilla HTML para una alerta de trabajo
        """
        try:
            template = jinja_env.get_template("job_alert.html")
        except Exception:
            # Fallback a plantilla básica si no existe archivo
            return self._get_fallback_job_template(user_name, job, notification)
        
        # Preparar datos para la plantilla
        salary_info = "No especificado"
        if job.salary_min and job.salary_max:
            salary_info = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
        elif job.salary_max:
            salary_info = f"Hasta ${job.salary_max:,.0f}"
        elif job.salary_min:
            salary_info = f"Desde ${job.salary_min:,.0f}"
        
        tech_stack_list = []
        if job.cleaned_stack:
            tech_stack_list = [tech.strip() for tech in job.cleaned_stack.split(',')]
        
        return template.render(
            user_name=user_name,
            job=job,
            notification=notification,
            salary_info=salary_info,
            tech_stack_list=tech_stack_list,
            is_golden_lead=notification.is_golden_lead,
            urgency_score=notification.urgency_score
        )
    
    def _render_market_signal_template(
        self, 
        user_name: str, 
        notification: Notification
    ) -> str:
        """
        Renderiza la plantilla HTML para una señal de mercado
        """
        try:
            template = jinja_env.get_template("market_signal.html")
        except Exception:
            return self._get_fallback_market_signal_template(user_name, notification)
        
        return template.render(
            user_name=user_name,
            notification=notification,
            metadata=notification.extra_data
        )
    
    def _get_fallback_job_template(
        self, 
        user_name: str, 
        job: Job, 
        notification: Notification
    ) -> str:
        """
        Plantilla HTML básica de fallback para alertas de trabajo
        """
        golden_badge = ""
        if notification.is_golden_lead:
            golden_badge = """
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                        padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                <h2 style="color: white; margin: 0; font-size: 24px;">🌟 GOLDEN LEAD 🌟</h2>
                <p style="color: white; margin: 5px 0 0 0;">Oportunidad Única - Alta Prioridad</p>
            </div>
            """
        
        salary_info = "No especificado"
        if job.salary_min and job.salary_max:
            salary_info = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
        elif job.salary_max:
            salary_info = f"Hasta ${job.salary_max:,.0f}"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; 
                        border-radius: 12px; padding: 30px; border: 1px solid #334155;">
                
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #0ea5e9; margin: 0; font-size: 28px;">Labortrovilo</h1>
                    <p style="color: #94a3b8; margin: 5px 0 0 0;">Tu portal de empleo tech</p>
                </div>
                
                {golden_badge}
                
                <!-- Greeting -->
                <p style="font-size: 16px; color: #e2e8f0;">Hola {user_name},</p>
                <p style="font-size: 16px; color: #e2e8f0;">
                    Hemos encontrado una nueva oportunidad que coincide con tus intereses:
                </p>
                
                <!-- Job Card -->
                <div style="background-color: #0f172a; border-radius: 8px; padding: 20px; 
                            border-left: 4px solid #0ea5e9; margin: 20px 0;">
                    <h2 style="color: #e2e8f0; margin: 0 0 15px 0; font-size: 22px;">{job.title}</h2>
                    
                    <p style="color: #94a3b8; margin: 5px 0;">
                        <strong style="color: #e2e8f0;">🏢 Empresa:</strong> {job.company_name}
                    </p>
                    
                    <p style="color: #94a3b8; margin: 5px 0;">
                        <strong style="color: #e2e8f0;">💰 Salario:</strong> {salary_info}
                    </p>
                    
                    <p style="color: #94a3b8; margin: 5px 0;">
                        <strong style="color: #e2e8f0;">💻 Tech Stack:</strong> {job.cleaned_stack or 'No especificado'}
                    </p>
                    
                    <div style="margin-top: 20px;">
                        <a href="{job.source_url}" 
                           style="display: inline-block; background-color: #0ea5e9; color: white; 
                                  padding: 12px 24px; text-decoration: none; border-radius: 6px; 
                                  font-weight: 600;">
                            Ver Oferta Completa
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #334155; 
                            text-align: center;">
                    <p style="color: #64748b; font-size: 14px; margin: 5px 0;">
                        © 2024 Labortrovilo. Todos los derechos reservados.
                    </p>
                    <p style="color: #64748b; font-size: 12px; margin: 5px 0;">
                        Para gestionar tus alertas, visita tu panel de control.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_fallback_market_signal_template(
        self, 
        user_name: str, 
        notification: Notification
    ) -> str:
        """
        Plantilla HTML básica de fallback para market signals
        """
        metadata = notification.extra_data or {}
        company_name = metadata.get('company_name', 'N/A')
        job_count = metadata.get('job_count', 0)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; 
                        border-radius: 12px; padding: 30px; border: 1px solid #334155;">
                
                <!-- Header -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #0ea5e9; margin: 0; font-size: 28px;">Labortrovilo</h1>
                    <p style="color: #94a3b8; margin: 5px 0 0 0;">Market Intelligence</p>
                </div>
                
                <!-- Alert Badge -->
                <div style="background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%); 
                            padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                    <h2 style="color: white; margin: 0; font-size: 24px;">🚀 Market Signal</h2>
                    <p style="color: white; margin: 5px 0 0 0;">Alta Velocidad de Contratación Detectada</p>
                </div>
                
                <!-- Greeting -->
                <p style="font-size: 16px; color: #e2e8f0;">Hola {user_name},</p>
                <p style="font-size: 16px; color: #e2e8f0;">
                    Hemos detectado una señal importante en el mercado laboral:
                </p>
                
                <!-- Signal Details -->
                <div style="background-color: #0f172a; border-radius: 8px; padding: 20px; 
                            border-left: 4px solid #8b5cf6; margin: 20px 0;">
                    <h3 style="color: #e2e8f0; margin: 0 0 15px 0;">{company_name}</h3>
                    
                    <p style="color: #94a3b8; font-size: 16px; line-height: 1.6;">
                        Ha publicado <strong style="color: #0ea5e9;">{job_count} puestos</strong> 
                        en las últimas 24 horas.
                    </p>
                    
                    <p style="color: #94a3b8; font-size: 14px; margin-top: 15px;">
                        Esto indica:
                    </p>
                    <ul style="color: #94a3b8; line-height: 1.8;">
                        <li>Alta actividad de contratación</li>
                        <li>Posible expansión del equipo</li>
                        <li>Oportunidad de networking</li>
                    </ul>
                </div>
                
                <!-- Footer -->
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #334155; 
                            text-align: center;">
                    <p style="color: #64748b; font-size: 14px; margin: 5px 0;">
                        © 2024 Labortrovilo. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """


class SlackNotifier:
    """
    Gestor de notificaciones vía Slack Webhooks
    """
    
    def send_job_alert(
        self, 
        webhook_url: str, 
        job: Job, 
        notification: Notification
    ) -> bool:
        """
        Envía una alerta de trabajo a Slack
        """
        try:
            # Construir mensaje Slack
            salary_info = "No especificado"
            if job.salary_min and job.salary_max:
                salary_info = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
            elif job.salary_max:
                salary_info = f"Hasta ${job.salary_max:,.0f}"
            
            # Emoji según tipo de notificación
            emoji = "💼"
            if notification.is_golden_lead:
                emoji = "🌟"
            elif notification.notification_type == "MARKET_SIGNAL":
                emoji = "🚀"
            
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} {notification.title}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Empresa:*\n{job.company_name}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Salario:*\n{salary_info}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Tech Stack:*\n{job.cleaned_stack or 'No especificado'}"
                            }
                        ]
                    }
                ]
            }
            
            # Agregar sección especial para Golden Leads
            if notification.is_golden_lead:
                payload["blocks"].insert(1, {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":star2: *OPORTUNIDAD ÚNICA* - Esta oferta cumple con criterios excepcionales"
                    }
                })
            
            # Agregar botón para ver oferta
            payload["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ver Oferta Completa"
                        },
                        "url": job.source_url,
                        "style": "primary"
                    }
                ]
            })
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Mensaje enviado a Slack exitosamente")
                return True
            else:
                logger.error(f"Error enviando a Slack: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando mensaje a Slack: {str(e)}", exc_info=True)
            return False
    
    def send_market_signal(
        self, 
        webhook_url: str, 
        notification: Notification
    ) -> bool:
        """
        Envía una señal de mercado a Slack
        """
        try:
            metadata = notification.extra_data or {}
            company_name = metadata.get('company_name', 'N/A')
            job_count = metadata.get('job_count', 0)
            
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚀 {notification.title}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{company_name}* ha publicado *{job_count} puestos* en las últimas 24 horas.\n\n"
                                   "Esto indica:\n• Alta actividad de contratación\n• Posible expansión del equipo\n• Oportunidad de networking"
                        }
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Market signal enviado a Slack exitosamente")
                return True
            else:
                logger.error(f"Error enviando market signal a Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando market signal a Slack: {str(e)}", exc_info=True)
            return False


class DiscordNotifier:
    """
    Gestor de notificaciones vía Discord Webhooks
    """
    
    def send_job_alert(
        self, 
        webhook_url: str, 
        job: Job, 
        notification: Notification
    ) -> bool:
        """
        Envía una alerta de trabajo a Discord
        """
        try:
            salary_info = "No especificado"
            if job.salary_min and job.salary_max:
                salary_info = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
            elif job.salary_max:
                salary_info = f"Hasta ${job.salary_max:,.0f}"
            
            # Color del embed según tipo
            color = 0x0ea5e9  # Blue
            if notification.is_golden_lead:
                color = 0xf59e0b  # Gold
            
            embed = {
                "title": notification.title,
                "url": job.source_url,
                "color": color,
                "fields": [
                    {
                        "name": "🏢 Empresa",
                        "value": job.company_name,
                        "inline": True
                    },
                    {
                        "name": "💰 Salario",
                        "value": salary_info,
                        "inline": True
                    },
                    {
                        "name": "💻 Tech Stack",
                        "value": job.cleaned_stack or "No especificado",
                        "inline": False
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if notification.is_golden_lead:
                embed["description"] = "🌟 **OPORTUNIDAD ÚNICA** - Esta oferta cumple con criterios excepcionales"
                embed["footer"] = {
                    "text": f"Urgency Score: {notification.urgency_score:.2f}"
                }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"Mensaje enviado a Discord exitosamente")
                return True
            else:
                logger.error(f"Error enviando a Discord: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando mensaje a Discord: {str(e)}", exc_info=True)
            return False
    
    def send_market_signal(
        self, 
        webhook_url: str, 
        notification: Notification
    ) -> bool:
        """
        Envía una señal de mercado a Discord
        """
        try:
            metadata = notification.extra_data or {}
            company_name = metadata.get('company_name', 'N/A')
            job_count = metadata.get('job_count', 0)
            
            embed = {
                "title": notification.title,
                "description": f"**{company_name}** ha publicado **{job_count} puestos** en las últimas 24 horas.",
                "color": 0x8b5cf6,  # Purple
                "fields": [
                    {
                        "name": "Implicaciones",
                        "value": "• Alta actividad de contratación\n• Posible expansión del equipo\n• Oportunidad de networking",
                        "inline": False
                    }
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Market Intelligence by Labortrovilo"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"Market signal enviado a Discord exitosamente")
                return True
            else:
                logger.error(f"Error enviando market signal a Discord: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando market signal a Discord: {str(e)}", exc_info=True)
            return False


class NotificationDispatcher:
    """
    Despachador central de notificaciones
    Coordina el envío a través de múltiples canales
    """
    
    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()
        self.discord_notifier = DiscordNotifier()
    
    def dispatch_notification(
        self, 
        notification: Notification, 
        user: User,
        job: Optional[Job] = None,
        config = None
    ) -> bool:
        """
        Envía una notificación por el canal especificado
        
        Returns:
            True si se envió exitosamente
        """
        try:
            if notification.channel == NotificationChannel.EMAIL:
                if notification.notification_type == "MARKET_SIGNAL":
                    return self.email_notifier.send_market_signal(
                        to_email=user.email,
                        user_name=user.full_name or user.email,
                        notification=notification
                    )
                else:
                    if not job:
                        logger.error(f"Job requerido para notificación tipo {notification.notification_type}")
                        return False
                    
                    return self.email_notifier.send_job_alert(
                        to_email=user.email,
                        user_name=user.full_name or user.email,
                        job=job,
                        notification=notification
                    )
            
            elif notification.channel == NotificationChannel.SLACK:
                if not config or not config.slack_webhook_url:
                    logger.warning(f"Slack webhook no configurado para usuario {user.id}")
                    return False
                
                if notification.notification_type == "MARKET_SIGNAL":
                    return self.slack_notifier.send_market_signal(
                        webhook_url=config.slack_webhook_url,
                        notification=notification
                    )
                else:
                    if not job:
                        logger.error(f"Job requerido para notificación tipo {notification.notification_type}")
                        return False
                    
                    return self.slack_notifier.send_job_alert(
                        webhook_url=config.slack_webhook_url,
                        job=job,
                        notification=notification
                    )
            
            elif notification.channel == NotificationChannel.DISCORD:
                if not config or not config.discord_webhook_url:
                    logger.warning(f"Discord webhook no configurado para usuario {user.id}")
                    return False
                
                if notification.notification_type == "MARKET_SIGNAL":
                    return self.discord_notifier.send_market_signal(
                        webhook_url=config.discord_webhook_url,
                        notification=notification
                    )
                else:
                    if not job:
                        logger.error(f"Job requerido para notificación tipo {notification.notification_type}")
                        return False
                    
                    return self.discord_notifier.send_job_alert(
                        webhook_url=config.discord_webhook_url,
                        job=job,
                        notification=notification
                    )
            
            else:
                logger.error(f"Canal de notificación no soportado: {notification.channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error despachando notificación {notification.id}: {str(e)}", exc_info=True)
            return False


if __name__ == "__main__":
    # Test básico
    print("Módulo de canales de notificación cargado correctamente")
