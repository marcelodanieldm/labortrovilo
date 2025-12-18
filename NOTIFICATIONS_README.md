# 🔔 Sistema de Notificaciones de Labortrovilo

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso de la API](#uso-de-la-api)
- [Canales de Notificación](#canales-de-notificación)
- [Sistema de Alertas](#sistema-de-alertas)
- [Scheduler y Automatización](#scheduler-y-automatización)
- [Golden Leads](#golden-leads)
- [Troubleshooting](#troubleshooting)

---

## 📖 Descripción General

El sistema de notificaciones de Labortrovilo es una solución completa de alertas inteligentes que:

✅ **Monitorea ofertas de empleo** en tiempo real según criterios personalizados  
✅ **Detecta Golden Leads** - oportunidades excepcionales con alta urgencia  
✅ **Genera Market Signals** - señales de alta actividad de contratación  
✅ **Envía notificaciones** por Email, Slack y Discord  
✅ **Automatiza el flujo completo** con APScheduler  

### 🎯 Flujo del Sistema

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Scraper   │─────▶│ AI Processor │─────▶│ AlertManager│─────▶│ Notificación │
│  (engine.py)│      │(ai_processor)│      │ (checks)    │      │   Channels   │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
       ↑                     ↑                     ↑                     ↑
       │                     │                     │                     │
       └─────────────────────┴─────────────────────┴─────────────────────┘
                          APScheduler (scheduler.py)
```

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### 1. **AlertManager** (`src/notifications.py`)
- Revisa nuevas ofertas contra configuraciones de usuarios
- Identifica Golden Leads (urgency_score > 0.9)
- Genera Market Signals (3+ jobs en 24h)
- Crea notificaciones en base de datos

#### 2. **NotificationChannels** (`src/notification_channels.py`)
- **EmailNotifier**: SendGrid + plantillas HTML Jinja2
- **SlackNotifier**: Webhooks con bloques interactivos
- **DiscordNotifier**: Webhooks con embeds coloridos

#### 3. **TaskOrchestrator** (`src/scheduler.py`)
- APScheduler con trabajos programados
- Ejecuta scraper cada 6 horas
- Revisa alertas cada hora
- Envía notificaciones cada 15 minutos
- Limpieza diaria de notificaciones antiguas

#### 4. **API Router** (`src/alerts_router.py`)
- CRUD de configuraciones de alertas
- Historial de notificaciones
- Estadísticas de alertas
- Endpoints de administración

### Base de Datos

#### Tabla: `alert_configs`
```python
user_id: int (FK)
tech_stack: JSON         # ["Python", "React"]
keywords: JSON           # ["senior", "lead"]
salary_min: int          # 80000
salary_max: int          # 150000
modality: str            # "remoto"
channels: JSON           # ["EMAIL", "SLACK"]
frequency: Enum          # IMMEDIATE, HOURLY, DAILY, WEEKLY
market_signals_enabled: bool
golden_leads_only: bool
slack_webhook_url: str
discord_webhook_url: str
is_active: bool
```

#### Tabla: `notifications`
```python
user_id: int (FK)
job_id: int (FK)
notification_type: str    # JOB_ALERT, MARKET_SIGNAL
title: str
message: str
channel: Enum            # EMAIL, SLACK, DISCORD
is_sent: bool
sent_at: datetime
is_golden_lead: bool
urgency_score: float     # 0.0 - 1.0
metadata: JSON
```

---

## ⚙️ Instalación y Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nuevas dependencias:**
- `apscheduler>=3.10.4` - Programación de tareas
- `celery>=5.3.4` - Cola de tareas distribuida
- `redis>=5.0.1` - Backend de Celery
- `sendgrid>=6.11.0` - Envío de emails
- `jinja2>=3.1.2` - Plantillas HTML

### 2. Configurar Variables de Entorno

Copia `.env.notifications.example` a `.env` y configura:

```bash
# SendGrid API Key (obtener de https://app.sendgrid.com/)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@labortrovilo.com

# Timezone
SCHEDULER_TIMEZONE=America/Mexico_City
```

### 3. Inicializar Base de Datos

```bash
# Crear tablas (User, AlertConfig, Notification)
python -c "from database import init_db; init_db()"
```

### 4. Crear Usuario de Prueba

```python
from database import SessionLocal
from models import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
user = User(
    email="test@labortrovilo.com",
    hashed_password=pwd_context.hash("test123"),
    role=UserRole.CANDIDATO,
    full_name="Test User",
    is_active=True
)
db.add(user)
db.commit()
print(f"Usuario creado: {user.email}")
```

---

## 🔌 Uso de la API

### Autenticación

Todos los endpoints requieren autenticación JWT:

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@labortrovilo.com&password=test123"

# Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "CANDIDATO"
}
```

### Crear Configuración de Alertas

```bash
curl -X POST http://localhost:8000/api/v1/alerts/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tech_stack": ["Python", "FastAPI", "React"],
    "keywords": ["senior", "lead"],
    "salary_min": 80000,
    "salary_max": 150000,
    "modality": "remoto",
    "channels": ["EMAIL", "SLACK"],
    "frequency": "DAILY",
    "market_signals_enabled": true,
    "golden_leads_only": false,
    "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }'
```

### Obtener Configuración Actual

```bash
curl -X GET http://localhost:8000/api/v1/alerts/config \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Actualizar Configuración

```bash
curl -X PUT http://localhost:8000/api/v1/alerts/config/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "salary_min": 100000,
    "golden_leads_only": true
  }'
```

### Activar/Desactivar Alertas

```bash
curl -X POST http://localhost:8000/api/v1/alerts/config/1/toggle \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ver Historial de Notificaciones

```bash
curl -X GET "http://localhost:8000/api/v1/alerts/notifications?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Solo Golden Leads
curl -X GET "http://localhost:8000/api/v1/alerts/notifications?only_golden_leads=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Estadísticas de Alertas

```bash
curl -X GET http://localhost:8000/api/v1/alerts/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# Respuesta:
{
  "total_notifications": 45,
  "notifications_sent": 40,
  "notifications_pending": 5,
  "golden_leads_count": 3,
  "last_alert_sent": "2024-01-15T10:30:00",
  "active_config": true
}
```

---

## 📧 Canales de Notificación

### Email (SendGrid)

**Características:**
- Plantillas HTML profesionales con diseño dark mode
- Badge especial para Golden Leads
- Visualización de tech stack con colores
- Responsive design
- Links directos a ofertas

**Configuración:**
1. Crear cuenta en [SendGrid](https://sendgrid.com/)
2. Obtener API Key en Settings > API Keys
3. Agregar API Key a `.env`:
   ```bash
   SENDGRID_API_KEY=SG.xxxxx
   ```

**Plantillas:**
- `src/templates/email/job_alert.html` - Alertas de trabajo
- `src/templates/email/market_signal.html` - Señales de mercado

### Slack

**Características:**
- Bloques interactivos con formato profesional
- Botones de acción directa
- Emojis contextuales
- Notificaciones agrupadas

**Configuración:**
1. Ir a tu workspace de Slack
2. Apps > Incoming Webhooks
3. Crear nuevo webhook
4. Copiar URL y agregarla en tu configuración de alertas:
   ```json
   {
     "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   }
   ```

**Formato de Mensaje:**
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🌟 Senior Python Developer"
      }
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Empresa:*\nTech Corp"},
        {"type": "mrkdwn", "text": "*Salario:*\n$120,000 - $150,000"}
      ]
    }
  ]
}
```

### Discord

**Características:**
- Embeds con colores personalizados
- Metadata en footer
- Timestamps automáticos
- Formato rich text

**Configuración:**
1. Server Settings > Integrations > Webhooks
2. New Webhook
3. Copiar Webhook URL
4. Agregar en configuración:
   ```json
   {
     "discord_webhook_url": "https://discord.com/api/webhooks/YOUR/ID"
   }
   ```

**Formato de Embed:**
```json
{
  "embeds": [{
    "title": "Senior Python Developer",
    "url": "https://job-url.com",
    "color": 0x0ea5e9,
    "fields": [
      {"name": "🏢 Empresa", "value": "Tech Corp", "inline": true},
      {"name": "💰 Salario", "value": "$120k - $150k", "inline": true}
    ],
    "timestamp": "2024-01-15T10:30:00.000Z"
  }]
}
```

---

## 🎯 Sistema de Alertas

### Tipos de Alertas

#### 1. **JOB_ALERT** (Candidatos)
Notificaciones de ofertas que coinciden con criterios:
- Tech stack match
- Rango salarial
- Keywords en título/descripción
- Modalidad de trabajo

**Algoritmo:**
```python
def matches_criteria(job, config):
    # Tech stack (ANY match)
    if config.tech_stack:
        job_techs = set(job.cleaned_stack.split(','))
        config_techs = set(config.tech_stack)
        if not job_techs.intersection(config_techs):
            return False
    
    # Salary range
    if config.salary_min and job.salary_max:
        if job.salary_max < config.salary_min:
            return False
    
    # Keywords
    if config.keywords:
        text = f"{job.title} {job.description}".lower()
        if not any(kw.lower() in text for kw in config.keywords):
            return False
    
    return True
```

#### 2. **MARKET_SIGNAL** (HR Professionals)
Señales de alta actividad de contratación:
- 3+ ofertas de la misma empresa en 24h
- Indica expansión o crecimiento
- Útil para networking y análisis de mercado

**SQL Query:**
```sql
SELECT company_name, COUNT(*) as job_count
FROM jobs
WHERE scraped_date >= NOW() - INTERVAL '24 hours'
GROUP BY company_name
HAVING COUNT(*) >= 3
ORDER BY job_count DESC
```

#### 3. **GOLDEN_LEAD** (Premium)
Oportunidades excepcionales que cumplen:
- `urgency_score > 0.9`
- `growth_score > 0.7`
- `salary_max > $100,000`
- Tech stack altamente demandado

**Cálculo de Urgency Score:**
```python
def calculate_urgency_score(job):
    score = 0.0
    
    # Recency (40% weight)
    hours_old = (now - job.scraped_date).total_seconds() / 3600
    if hours_old < 24:
        score += 0.4 * (1 - hours_old / 24)
    
    # Urgency keywords (30% weight)
    urgency_keywords = ['urgente', 'asap', 'inmediato', 'start now']
    if any(kw in job.description.lower() for kw in urgency_keywords):
        score += 0.3
    
    # High salary (30% weight)
    if job.salary_max and job.salary_max > 120000:
        score += 0.3
    
    return min(score, 1.0)
```

### Frecuencia de Alertas

| Frecuencia | Descripción | Uso Recomendado |
|-----------|-------------|-----------------|
| `IMMEDIATE` | Notificación inmediata (< 15 min) | Golden Leads, ofertas urgentes |
| `HOURLY` | Resumen cada hora | Búsqueda activa de empleo |
| `DAILY` | Digest diario (9 AM) | Monitoreo pasivo |
| `WEEKLY` | Resumen semanal (Lunes 9 AM) | Market intelligence |

---

## ⏱️ Scheduler y Automatización

### Iniciar Scheduler

```bash
# Modo producción (background)
python src/scheduler.py start

# Modo test (una ejecución)
python src/scheduler.py test
```

### Trabajos Programados

| Trabajo | Frecuencia | Descripción |
|---------|-----------|-------------|
| `scraper_job` | Cada 6 horas | Ejecuta engine.py para scraping |
| `ai_processor_job` | 6h + 15min | Procesa ofertas con AI |
| `alert_check_job` | Cada hora | Revisa nuevas ofertas vs configuraciones |
| `send_notifications_job` | Cada 15 min | Envía notificaciones pendientes |
| `cleanup_job` | Diario 3 AM | Elimina notificaciones antiguas (>30 días) |
| `daily_stats_job` | Diario 9 AM | Genera reporte de estadísticas |

### Control Manual

```python
from src.scheduler import get_orchestrator

orchestrator = get_orchestrator()

# Pausar un trabajo
orchestrator.pause_job('scraper_job')

# Reanudar un trabajo
orchestrator.resume_job('scraper_job')

# Ejecutar manualmente
orchestrator.trigger_job_now('alert_check_job')

# Detener scheduler
orchestrator.stop()
```

### Logs

Monitorear logs del scheduler:

```bash
tail -f logs/notifications.log

# Salida esperada:
2024-01-15 10:00:00 - INFO - =========================
2024-01-15 10:00:00 - INFO - INICIANDO: Alert Check Job
2024-01-15 10:00:00 - INFO - =========================
2024-01-15 10:00:05 - INFO - Resultados:
2024-01-15 10:00:05 - INFO -   - Jobs revisados: 25
2024-01-15 10:00:05 - INFO -   - Alertas candidatos: 12
2024-01-15 10:00:05 - INFO -   - Golden Leads: 2
2024-01-15 10:00:05 - INFO -   - Total notificaciones: 14
```

---

## 🌟 Golden Leads

### ¿Qué son?

**Golden Leads** son ofertas excepcionales que cumplen criterios de alta calidad:

✅ **Alta urgencia** - Publicadas recientemente, palabras clave urgentes  
✅ **Empresa en crecimiento** - Múltiples contrataciones activas  
✅ **Salario competitivo** - Por encima del mercado  
✅ **Tech stack moderno** - Tecnologías demandadas  

### Criterios de Identificación

```python
def is_golden_lead(job, company_stats):
    # Urgency score > 0.9
    urgency = calculate_urgency_score(job)
    if urgency <= 0.9:
        return False
    
    # Growth score > 0.7
    growth = calculate_growth_score(company_stats)
    if growth <= 0.7:
        return False
    
    # Salary > $100k
    if not job.salary_max or job.salary_max <= 100000:
        return False
    
    return True
```

### Notificaciones Especiales

Golden Leads reciben tratamiento premium:

#### Email
- Badge dorado destacado
- Prioridad en la bandeja de entrada
- Diseño especial con gradiente dorado
- Consejos adicionales para aplicar

#### Slack
- Emoji de estrella 🌟
- Mensaje con estilo destacado
- Botón de "Alta Prioridad"

#### Discord
- Color dorado (#f59e0b)
- Footer con urgency score
- Ping opcional (@here)

### Configuración

```json
{
  "golden_leads_only": true,    // Solo recibir Golden Leads
  "frequency": "IMMEDIATE"      // Notificación instantánea
}
```

---

## 🔧 Troubleshooting

### Problema: No llegan emails

**Diagnóstico:**
1. Verificar API Key de SendGrid
2. Revisar logs: `tail -f logs/notifications.log`
3. Verificar dominio remitente verificado

**Solución:**
```bash
# Test de envío
python -c "
from src.notification_channels import EmailNotifier
notifier = EmailNotifier()
print('API Key configurada:', bool(notifier.api_key))
"
```

### Problema: Scheduler no ejecuta trabajos

**Diagnóstico:**
1. Verificar que scheduler esté corriendo: `ps aux | grep scheduler`
2. Revisar timezone configurado
3. Verificar próxima ejecución

**Solución:**
```python
from src.scheduler import get_orchestrator
orchestrator = get_orchestrator()
orchestrator.start()
orchestrator._print_scheduled_jobs()
```

### Problema: Notificaciones duplicadas

**Causa:** El sistema usa `check_duplicate_notification()` pero puede haber race conditions.

**Solución:**
```python
# Revisar duplicados
from database import SessionLocal
from models import Notification

db = SessionLocal()
duplicates = db.execute("""
    SELECT user_id, job_id, COUNT(*) as count
    FROM notifications
    GROUP BY user_id, job_id
    HAVING COUNT(*) > 1
""").fetchall()

# Eliminar duplicados (mantener el más reciente)
for user_id, job_id, count in duplicates:
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.job_id == job_id
    ).order_by(Notification.created_at.desc()).all()
    
    for notif in notifications[1:]:  # Eliminar todos excepto el primero
        db.delete(notif)
    
db.commit()
```

### Problema: Webhook de Slack/Discord falla

**Diagnóstico:**
```bash
# Test manual
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test from Labortrovilo"}'
```

**Errores comunes:**
- URL incorrecta (copiar bien el webhook)
- Permisos revocados (regenerar webhook)
- Timeout de red (verificar conectividad)

---

## 📊 Métricas y Monitoreo

### Dashboard de Admin

```bash
curl -X GET http://localhost:8000/api/v1/alerts/admin/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Respuesta:**
```json
{
  "total_alert_configs": 156,
  "active_alert_configs": 142,
  "total_notifications": 4523,
  "notifications_sent": 4234,
  "notifications_pending": 289,
  "golden_leads_identified": 87
}
```

### KPIs Importantes

| Métrica | Target | Descripción |
|---------|--------|-------------|
| **Delivery Rate** | > 95% | % notificaciones enviadas exitosamente |
| **Golden Lead Ratio** | 2-5% | % de ofertas identificadas como Golden Leads |
| **Avg Response Time** | < 15 min | Tiempo desde creación hasta envío |
| **User Engagement** | > 60% | % usuarios con alertas activas |

---

## 🚀 Próximos Pasos

1. **Integrar con Frontend React**
   - Pantalla de configuración de alertas
   - Historial visual de notificaciones
   - Dashboard de Golden Leads

2. **Machine Learning**
   - Personalización de urgency score
   - Recomendaciones de tech stack
   - Predicción de salarios

3. **Webhooks Salientes**
   - Permitir a usuarios definir webhooks propios
   - Integración con Zapier/Make
   - API para aplicaciones terceras

4. **Mobile Push Notifications**
   - Firebase Cloud Messaging
   - iOS/Android apps

---

## 📞 Soporte

Para ayuda o reportar bugs:
- **Email**: support@labortrovilo.com
- **GitHub Issues**: github.com/labortrovilo/issues
- **Slack**: labortrovilo.slack.com

---

**© 2024 Labortrovilo. Todos los derechos reservados.**
