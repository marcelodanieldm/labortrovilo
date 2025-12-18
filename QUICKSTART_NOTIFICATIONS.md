# 🚀 Guía Rápida - Sistema de Notificaciones

## ⚙️ Setup Inicial

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.notifications.example .env

# Editar .env y agregar tu SendGrid API Key
# SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
```

### 3. Inicializar base de datos
```bash
python -c "from database import init_db; init_db()"
```

### 4. Ejecutar tests
```bash
python test_notifications.py
```

---

## 🔥 Comandos Rápidos

### Iniciar API con notificaciones
```bash
# Terminal 1: API FastAPI
uvicorn src.main:app --reload

# Terminal 2: Scheduler (automatización)
python src/scheduler.py start
```

### Test manual de componentes
```bash
# Test AlertManager
python -c "
from src.notifications import AlertManager
manager = AlertManager()
stats = manager.check_new_jobs_for_alerts(hours_lookback=24)
print(stats)
"

# Test Email Notifier
python -c "
from src.notification_channels import EmailNotifier
notifier = EmailNotifier()
print('API Key configurada:', bool(notifier.api_key))
"

# Test Scheduler (una vez)
python src/scheduler.py test
```

---

## 📧 Configurar Alertas (API)

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=tu_email@ejemplo.com&password=tu_password"
```

**Guarda el `access_token` de la respuesta**

### 2. Crear configuración de alertas
```bash
export TOKEN="tu_access_token_aqui"

curl -X POST http://localhost:8000/api/v1/alerts/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tech_stack": ["Python", "FastAPI", "React"],
    "keywords": ["senior", "lead"],
    "salary_min": 80000,
    "salary_max": 150000,
    "modality": "remoto",
    "channels": ["EMAIL"],
    "frequency": "DAILY",
    "market_signals_enabled": true,
    "golden_leads_only": false
  }'
```

### 3. Ver tu configuración
```bash
curl -X GET http://localhost:8000/api/v1/alerts/config \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Ver notificaciones recibidas
```bash
curl -X GET http://localhost:8000/api/v1/alerts/notifications \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Ver estadísticas
```bash
curl -X GET http://localhost:8000/api/v1/alerts/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔔 Configurar Canales

### Email (SendGrid)
1. Crear cuenta en [SendGrid](https://sendgrid.com/)
2. Obtener API Key en Settings > API Keys
3. Agregar a `.env`:
```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@tudominio.com
```

### Slack
1. Ir a tu workspace de Slack
2. Apps > Incoming Webhooks
3. Crear webhook y copiar URL
4. Agregar en tu configuración:
```json
{
  "channels": ["EMAIL", "SLACK"],
  "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

### Discord
1. Server Settings > Integrations > Webhooks
2. New Webhook
3. Copiar URL
4. Agregar en configuración:
```json
{
  "channels": ["EMAIL", "DISCORD"],
  "discord_webhook_url": "https://discord.com/api/webhooks/YOUR/ID"
}
```

---

## 🔍 Monitoreo y Logs

### Ver logs del scheduler
```bash
tail -f logs/notifications.log
```

### Ver trabajos programados
```python
from src.scheduler import get_orchestrator

orchestrator = get_orchestrator()
orchestrator.start()
orchestrator._print_scheduled_jobs()
```

### Ejecutar trabajo manualmente
```python
from src.scheduler import get_orchestrator

orchestrator = get_orchestrator()
orchestrator.start()

# Ejecutar check de alertas
orchestrator.trigger_job_now('alert_check_job')

# Enviar notificaciones pendientes
orchestrator.trigger_job_now('send_notifications_job')
```

---

## 🌟 Golden Leads

### Qué son
Ofertas excepcionales que cumplen:
- ✅ Alta urgencia (score > 0.9)
- ✅ Empresa en crecimiento
- ✅ Salario > $100,000
- ✅ Tech stack moderno

### Configurar solo Golden Leads
```bash
curl -X POST http://localhost:8000/api/v1/alerts/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tech_stack": ["Python", "React"],
    "salary_min": 100000,
    "golden_leads_only": true,
    "frequency": "IMMEDIATE",
    "channels": ["EMAIL", "SLACK"]
  }'
```

### Ver solo Golden Leads recibidos
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/notifications?only_golden_leads=true" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🛠️ Troubleshooting

### No llegan emails
```bash
# 1. Verificar API Key
python -c "
from src.notification_channels import EmailNotifier
n = EmailNotifier()
print('API Key configurada:', bool(n.api_key))
"

# 2. Verificar plantillas
ls src/templates/email/

# 3. Ver logs
tail -f logs/notifications.log | grep -i email
```

### Scheduler no ejecuta
```bash
# Verificar proceso
ps aux | grep scheduler

# Reiniciar
pkill -f scheduler.py
python src/scheduler.py start

# Test manual
python src/scheduler.py test
```

### Ver notificaciones pendientes
```python
from database import SessionLocal
from models import Notification

db = SessionLocal()
pending = db.query(Notification).filter(
    Notification.is_sent == False
).count()
print(f"Notificaciones pendientes: {pending}")
```

---

## 📊 Endpoints Útiles

### Swagger UI
```
http://localhost:8000/docs
```

### Principales endpoints
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/alerts/config` - Crear/actualizar alertas
- `GET /api/v1/alerts/config` - Ver configuración
- `GET /api/v1/alerts/notifications` - Historial
- `GET /api/v1/alerts/stats` - Estadísticas
- `POST /api/v1/alerts/config/{id}/toggle` - Activar/desactivar

---

## 🚀 Flujo Completo

### Desde cero hasta recibir notificaciones

1. **Setup inicial**
```bash
pip install -r requirements.txt
cp .env.notifications.example .env
# Editar .env con tu SendGrid API Key
python -c "from database import init_db; init_db()"
```

2. **Iniciar servicios**
```bash
# Terminal 1: API
uvicorn src.main:app --reload

# Terminal 2: Scheduler
python src/scheduler.py start
```

3. **Crear usuario y configurar alertas** (ver sección "Configurar Alertas")

4. **Ejecutar scraper** (genera ofertas)
```bash
python engine.py
```

5. **Revisar que hay notificaciones creadas**
```bash
curl -X GET http://localhost:8000/api/v1/alerts/notifications \
  -H "Authorization: Bearer $TOKEN"
```

6. **Las notificaciones se enviarán automáticamente cada 15 minutos** 📧

---

## 💡 Tips

### Desarrollo
- Usa `frequency: "IMMEDIATE"` para tests rápidos
- Configura solo `"channels": ["EMAIL"]` inicialmente
- Monitorea logs con `tail -f logs/notifications.log`

### Producción
- Usa `frequency: "DAILY"` o `"WEEKLY"` para evitar spam
- Configura múltiples canales: `["EMAIL", "SLACK"]`
- Activa `golden_leads_only: true` para alertas premium

### Performance
- El scheduler usa ThreadPoolExecutor para paralelismo
- Máximo 100 notificaciones por batch (configurable)
- Notificaciones antiguas se limpian automáticamente (>30 días)

---

**¿Preguntas?** Revisa `NOTIFICATIONS_README.md` para documentación completa.
