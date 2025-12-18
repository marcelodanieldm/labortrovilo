# 🚀 Labortrovilo REST API

**API REST profesional con autenticación JWT y roles jerárquicos**

[🇪🇸 Español](#español) | [🇪🇴 Esperanto](#esperanto) | [🇬🇧 English](#english)

---

## 🇪🇸 Español

### 📋 Descripción

API REST desarrollada con **FastAPI** que proporciona acceso programático a la base de datos de empleos de Labortrovilo. Implementa autenticación JWT con 4 niveles de roles jerárquicos y control de acceso basado en permisos.

### ✨ Características Principales

#### 🔐 Sistema de Autenticación
- **JWT (JSON Web Tokens)** con OAuth2 Password Flow
- Tokens con expiración de 24 horas
- Hashing seguro de passwords con bcrypt
- Schema estándar OAuth2PasswordBearer

#### 👥 Sistema de Roles (Jerarquía)

```
SUPERUSER (Nivel 4) ← Acceso completo
    ↑
ADMIN (Nivel 3) ← Gestión de scrapers + todo lo de HR_PRO
    ↑
HR_PRO (Nivel 2) ← Analíticas premium + descarga de datos
    ↑
CANDIDATO (Nivel 1) ← Búsqueda básica de empleos
```

**Roles disponibles:**

1. **CANDIDATO** (Nivel 1)
   - Búsqueda y filtrado de empleos públicos
   - Vista limitada de campos (sin `red_flags`, `hiring_intent`)
   
2. **HR_PRO** (Nivel 2)
   - Todo lo de CANDIDATO +
   - Market Intelligence (analíticas de mercado)
   - Descarga de dataset (DaaS - Data as a Service)
   - Acceso a todos los campos de Job
   
3. **ADMIN** (Nivel 3)
   - Todo lo de HR_PRO +
   - Dashboard de scrapers
   - Estadísticas de sistema
   - Gestión de scraping
   
4. **SUPERUSER** (Nivel 4)
   - Acceso completo a toda la API
   - Dashboard de billing
   - Métricas globales de uso
   - Gestión de usuarios (futuro)

### 📍 Endpoints Principales

#### Autenticación

**POST /api/v1/auth/login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=candidato&password=password123"
```

Respuesta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "candidato",
    "email": "candidato@example.com",
    "full_name": "Juan Candidato",
    "role": "CANDIDATO"
  }
}
```

**GET /api/v1/auth/me**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Endpoints por Rol

##### 🔹 CANDIDATO (Nivel 1)

**GET /api/v1/jobs** - Búsqueda de empleos
```bash
curl -X GET "http://localhost:8000/api/v1/jobs?limit=10&company=Google" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Parámetros de filtrado:
- `page`: Número de página (default: 1)
- `page_size`: Resultados por página (default: 20, max: 100)
- `company`: Filtrar por nombre de empresa
- `location`: Filtrar por ubicación
- `title`: Filtrar por título de puesto
- `min_urgency`: Score mínimo de urgencia (0.0-1.0)

##### 🔹 HR_PRO (Nivel 2+)

**GET /api/v1/market-intelligence** - Analíticas de mercado
```bash
curl -X GET "http://localhost:8000/api/v1/market-intelligence?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Datos incluidos:
- Total de empleos activos
- Empresas que más contratan
- Score promedio de urgencia
- Tendencias de contratación

**GET /api/v1/dataset** - Descarga de datos (DaaS)
```bash
curl -X GET "http://localhost:8000/api/v1/dataset?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o jobs_dataset.json
```

Incluye:
- Últimos 100 empleos procesados con IA
- Todos los campos premium (red_flags, hiring_intent, etc.)
- Metadatos del dataset (versión, timestamp)

##### 🔹 ADMIN (Nivel 3+)

**GET /api/v1/admin/scrapers** - Dashboard de scrapers
```bash
curl -X GET "http://localhost:8000/api/v1/admin/scrapers" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Información:
- Estado de todos los scrapers
- Empleos scrapeados por fuente
- Tasa de éxito/error
- Salud del sistema

##### 🔹 SUPERUSER (Nivel 4)

**GET /api/v1/superuser/billing** - Dashboard ejecutivo
```bash
curl -X GET "http://localhost:8000/api/v1/superuser/billing" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Métricas globales:
- Revenue total y MRR
- Usuarios activos por rol
- Uptime del sistema
- Uso de API por endpoint

### 🔧 Instalación y Ejecución

#### 1. Instalar dependencias
```bash
pip install fastapi uvicorn[standard] python-jose[cryptography] passlib[bcrypt] python-multipart email-validator
```

#### 2. Ejecutar servidor
```bash
# Opción 1: Script quick-start
python run_api.py

# Opción 2: Uvicorn directo
uvicorn src.main:app --reload --port 8000
```

#### 3. Acceder a la documentación
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 👤 Usuarios de Demo

| Username   | Password      | Rol        | Nivel |
|-----------|---------------|------------|-------|
| candidato | password123   | CANDIDATO  | 1     |
| hr_pro    | hrpass123     | HR_PRO     | 2     |
| admin     | adminpass123  | ADMIN      | 3     |
| superuser | superpass123  | SUPERUSER  | 4     |

### 🧪 Testing

#### Ejecutar test suite completo
```bash
python test_api.py
```

Este script ejecuta:
- ✅ Health check
- ✅ Login de todos los roles
- ✅ Tests de endpoints por rol
- ✅ Verificación de permisos (403 Forbidden cuando corresponde)
- ✅ Validación de campos visibles por rol

### 🏗️ Arquitectura

```
src/
├── auth.py           # Sistema de autenticación JWT
│   ├── UserRole enum (4 roles)
│   ├── create_access_token()
│   ├── decode_access_token()
│   ├── get_password_hash()
│   └── verify_password()
│
├── dependencies.py   # Middleware de FastAPI
│   ├── oauth2_scheme
│   ├── get_current_user()
│   ├── RoleChecker class
│   └── Dependency instances (require_*)
│
├── api_models.py     # Modelos Pydantic por rol
│   ├── JobPublicResponse (CANDIDATO)
│   ├── JobPremiumResponse (HR_PRO+)
│   ├── MarketIntelligenceResponse
│   ├── AdminScrapersDashboardResponse
│   └── SuperuserBillingResponse
│
└── main.py           # Aplicación FastAPI
    ├── /api/v1/auth/login
    ├── /api/v1/auth/me
    ├── /api/v1/jobs
    ├── /api/v1/market-intelligence
    ├── /api/v1/dataset
    ├── /api/v1/admin/scrapers
    └── /api/v1/superuser/billing
```

### 🔒 Seguridad

#### ⚠️ IMPORTANTE para Producción

1. **Cambiar SECRET_KEY**: 
   ```python
   # En .env o config.py
   SECRET_KEY = "tu-clave-secreta-super-segura-de-32-chars-minimo"
   ```
   
2. **Configurar CORS restrictivo**:
   ```python
   # En src/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://tu-dominio.com"],  # NO usar "*"
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["Authorization", "Content-Type"],
   )
   ```

3. **Reemplazar FAKE_USERS_DB**:
   - Crear tabla `Users` en la base de datos
   - Implementar registro de usuarios
   - Gestión de permisos dinámica

4. **Usar HTTPS en producción**:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 443 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

5. **Rate Limiting**: Agregar slowapi o similar
6. **Logging de seguridad**: Registrar intentos de login fallidos
7. **Rotación de tokens**: Implementar refresh tokens

### 📊 Modelo de Negocio DaaS

La API está diseñada para el modelo **Data as a Service**:

- **HR_PRO** puede descargar datos procesados con IA
- Endpoint `/api/v1/dataset` con últimos 100 empleos validados
- Incluye metadatos para tracking de descargas
- Ideal para integración con herramientas de BI/Analytics

### 🔗 Integración con AI Module

La API se integra perfectamente con el módulo de IA:

```python
from src.ai_processor import AIJobProcessor
from src.database import SessionLocal

# Procesar empleos con IA
processor = AIJobProcessor(provider="openai")
session = SessionLocal()

jobs = session.query(Job).filter(Job.ai_processed == False).limit(10).all()
for job in jobs:
    processor.enrich_job_data(job, session)
```

### 📚 Próximas Funcionalidades

- [ ] Endpoints de registro de usuarios
- [ ] Sistema de refresh tokens
- [ ] Webhooks para eventos (nuevo empleo, etc.)
- [ ] GraphQL API alternativa
- [ ] Paginación con cursors
- [ ] Búsqueda full-text con Elasticsearch
- [ ] Rate limiting por rol
- [ ] Notificaciones push

---

## 🇪🇴 Esperanto

### 📋 Priskribo

REST API evoluigita kun **FastAPI** kiu provizas programan aliron al la dungara datumbazo de Labortrovilo. Ĝi efektivigas JWT-aŭtentikigon kun 4 niveloj de hierarkiaj roloj kaj alirrégadon bazitan sur permesoj.

### 👤 Demo Uzantoj

| Uzantnomo | Pasvorto     | Rolo       | Nivelo |
|----------|--------------|------------|---------|
| candidato | password123  | KANDIDATO  | 1       |
| hr_pro    | hrpass123    | HR_PRO     | 2       |
| admin     | adminpass123 | ADMIN      | 3       |
| superuser | superpass123 | SUPERUSER  | 4       |

### 🚀 Ekzekuto

```bash
python run_api.py
```

Dokumentado: http://localhost:8000/docs

---

## 🇬🇧 English

### 📋 Description

REST API developed with **FastAPI** that provides programmatic access to Labortrovilo's job database. Implements JWT authentication with 4 hierarchical role levels and permission-based access control.

### ✨ Key Features

#### 🔐 Authentication System
- **JWT (JSON Web Tokens)** with OAuth2 Password Flow
- 24-hour token expiration
- Secure password hashing with bcrypt
- Standard OAuth2PasswordBearer scheme

#### 👥 Role System (Hierarchy)

```
SUPERUSER (Level 4) ← Full access
    ↑
ADMIN (Level 3) ← Scraper management + all HR_PRO
    ↑
HR_PRO (Level 2) ← Premium analytics + data download
    ↑
CANDIDATO (Level 1) ← Basic job search
```

### 👤 Demo Users

| Username  | Password     | Role       | Level |
|----------|--------------|------------|-------|
| candidato | password123  | CANDIDATO  | 1     |
| hr_pro    | hrpass123    | HR_PRO     | 2     |
| admin     | adminpass123 | ADMIN      | 3     |
| superuser | superpass123 | SUPERUSER  | 4     |

### 🚀 Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn[standard] python-jose[cryptography] passlib[bcrypt] python-multipart email-validator

# Run server
python run_api.py

# Open documentation
# http://localhost:8000/docs
```

### 📍 Main Endpoints

#### Authentication
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/auth/me` - Get current user info

#### CANDIDATO (Level 1)
- `GET /api/v1/jobs` - Search jobs (basic fields)

#### HR_PRO (Level 2+)
- `GET /api/v1/market-intelligence` - Market analytics
- `GET /api/v1/dataset` - Download data (DaaS)

#### ADMIN (Level 3+)
- `GET /api/v1/admin/scrapers` - Scraper dashboard

#### SUPERUSER (Level 4)
- `GET /api/v1/superuser/billing` - Executive dashboard

### 🧪 Testing

```bash
python test_api.py
```

### 🔒 Security Notes

**⚠️ Before production:**
1. Change `SECRET_KEY` in config
2. Restrict CORS origins
3. Replace `FAKE_USERS_DB` with real user table
4. Enable HTTPS
5. Implement rate limiting

### 📊 DaaS Business Model

The API supports a **Data as a Service** model:
- HR_PRO users can download AI-processed job data
- `/api/v1/dataset` endpoint with last 100 validated jobs
- Metadata for download tracking
- Ready for BI/Analytics tool integration

---

## 📄 Licencia / Permesilo / License

MIT License - Ver LICENSE file

---

**Desarrollado con ❤️ por el equipo de Labortrovilo**
