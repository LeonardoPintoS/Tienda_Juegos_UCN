# 🎮 GameVault UCN

Plataforma backend para **GameVault UCN**, un sistema de distribución digital de videojuegos. Esta API REST está construida con FastAPI y una arquitectura por capas (Routers, Servicios y Repositorios) para mantener un código escalable, mantenible y seguro.

Proyecto del **Taller 1 — Introducción al Desarrollo Web y Móvil**, Universidad Católica del Norte, segundo semestre 2026.

## 🚀 Tecnologías y Herramientas

- **Framework:** FastAPI (Python 3.12+)
- **Base de Datos:** SQLite
- **ORM:** SQLModel (sobre SQLAlchemy)
- **Migraciones:** Alembic
- **Autenticación:** JSON Web Tokens (JWT) con invalidación mediante Blacklist
- **Contraseñas:** hash con bcrypt
- **Limitación de tasa:** slowapi
- **Servicio de Correos:** Resend API (con modo de desarrollo que guarda los correos en disco)
- **Calidad de código:** Ruff y pre-commit con Conventional Commits
- **Próximamente:** Cloudinary (imágenes del catálogo) y APScheduler (tareas programadas)

## 🏗️ Arquitectura del Proyecto

El proyecto está dividido en capas, donde cada una solo habla con la siguiente:

- **Routers:** endpoints HTTP. Solo traducen la petición y la respuesta.
- **Services:** reglas de negocio. Son quienes hacen el commit de la transacción.
- **Repositories:** acceso a datos con el ORM. Nunca hacen commit.
- **Models:** entidades de la base de datos (15 tablas).
- **Schemas:** validación y forma de los datos de entrada y salida.
- **Core:** configuración, base de datos, seguridad, errores centralizados, dependencias de rol y rate limit.

```
app/
├── core/          configuración, base de datos, seguridad, errores, dependencias de rol, rate limit
├── models/        modelos SQLModel
├── schemas/       esquemas Pydantic
├── repositories/  acceso a datos
├── services/      reglas de negocio
├── routers/       endpoints HTTP
├── integrations/  Resend (y Cloudinary)
├── seeders/       datos de prueba
├── jobs/          tareas programadas
└── main.py        aplicación FastAPI
migrations/        migraciones de Alembic
```

## ⚙️ Requisitos Previos

- Python 3.12 o superior instalado.
- Git.
- Un editor compatible (VS Code, PyCharm).
- Opcional: cuenta activa en Resend (para enviar correos reales) y en Cloudinary.

## 🛠️ Instalación y Configuración Local

Sigue estos pasos estrictamente para ejecutar el proyecto en tu entorno local. Los comandos están pensados para Git Bash (Windows), Linux o macOS.

### 1. Clonar el repositorio

```bash
git clone https://github.com/LeonardoPintoS/Tienda_Juegos_UCN.git
cd Tienda_Juegos_UCN
git switch develop
```

Abre VS Code con el siguiente comando:

```bash
code .
```

### 2. Crear el entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/Scripts/activate      # Git Bash en Windows
# source .venv/bin/activate        # Linux o macOS
# .venv\Scripts\Activate.ps1       # PowerShell en Windows

pip install -r requirements.txt
```

### 3. Instalar los hooks de pre-commit

Revisan el estilo del código y que los mensajes de commit sigan Conventional Commits:

```bash
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

### 4. Configurar Variables de Entorno

Crea el archivo `.env` desde la terminal de VS Code:

```bash
cp .env.example .env
```

El archivo `.env` **nunca se sube a GitHub** (está en `.gitignore`). Todas las variables traen un valor de desarrollo, así que el proyecto levanta con el `.env.example` sin tocar nada. Para un uso real, genera tu propia clave secreta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Pega el resultado en `SECRET_KEY`.

### 5. Parámetros del Sistema (.env)

Todo el sistema se configura desde el `.env`, que actúa como el "panel de control": permite cambiar reglas críticas sin tocar el código. A continuación se detalla cada módulo.

#### 1. 🌐 Aplicación y Base de Datos

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `APP_NAME` | `GameVault UCN` | Nombre de la aplicación que aparece en Swagger. |
| `ENVIRONMENT` | `development` | `development` o `production`. En `production` la app se niega a arrancar si faltan credenciales reales de Resend y Cloudinary o si `SECRET_KEY` es la de ejemplo. |
| `DEBUG` | `true` | Si es `true`, imprime en consola todas las consultas SQL. |
| `CORS_ORIGINS` | `*` | Orígenes permitidos por CORS: `*` o una lista separada por comas. |
| `DATABASE_URL` | `sqlite:///./gamevault.db` | Cadena de conexión de la base de datos. |

#### 2. 🔐 Seguridad y Autenticación

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | valor de ejemplo | Clave con la que se firman los JWT. Debe ser propia y secreta. |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de firma del JWT. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Ciclo de vida de un token antes de obligar a iniciar sesión de nuevo. |
| `RATE_LIMIT_AUTH` | `5/minute` | Límite de solicitudes por IP en los endpoints `/auth`, contra fuerza bruta. |

#### 3. ✉️ Verificación de Correo

Protege el endpoint de confirmación de cuenta contra ataques de fuerza bruta.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `VERIFICATION_CODE_LENGTH` | `6` | Cantidad de dígitos del código. |
| `VERIFICATION_CODE_TTL_MINUTES` | `15` | Minutos de vigencia del código. |
| `VERIFICATION_MAX_ATTEMPTS` | `5` | Intentos fallidos antes de bloquear la verificación. |
| `VERIFICATION_BLOCK_MINUTES` | `30` | Minutos de bloqueo tras agotar los intentos. |
| `VERIFICATION_RESEND_COOLDOWN_SECONDS` | `60` | Espera mínima entre reenvíos del código. |
| `RESEND_API_KEY` | vacío | API key de [Resend](https://resend.com). Vacío activa el modo `dev-outbox`. |
| `RESEND_FROM_EMAIL` | `GameVault UCN <no-reply@gamevault.ucn.cl>` | Remitente de los correos. |

#### 4. 👥 Semilla de Datos y Usuarios

Controla los datos que el seeder inyecta automáticamente en la base de datos. Permite a los evaluadores probar los flujos de administración de inmediato.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SEED_ON_STARTUP` | `true` | Si es `true`, el servidor carga los datos de prueba al iniciar. |
| `ADMIN_EMAIL` | `admin@gamevault.ucn.cl` | Correo del administrador inicial. |
| `ADMIN_PASSWORD` | `ChangeMe123!` | Contraseña del administrador. Cámbiala. |
| `ADMIN_FULL_NAME` | `Administrador GameVault` | Nombre del administrador. |

#### 5. ⚙️ Tareas en Segundo Plano (reservado)

Estas variables ya están definidas, pero los jobs se activarán cuando se implemente el módulo de mantenimiento.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `SCHEDULER_ENABLED` | `true` | Activa los jobs programados. |
| `UNVERIFIED_ACCOUNT_TTL_HOURS` | `48` | Horas antes de eliminar una cuenta no verificada. |
| `BLACKLIST_PURGE_INTERVAL_HOURS` | `6` | Cada cuántas horas se purga la blacklist de tokens expirados. |
| `GUEST_CART_TTL_DAYS` | `30` | Días de vida del carrito de un invitado. |

#### 6. 🖼️ Imágenes del Catálogo (Cloudinary)

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `CLOUDINARY_CLOUD_NAME` | vacío | Nombre de la cuenta. Vacío activa el modo `dev-local`. |
| `CLOUDINARY_API_KEY` | vacío | API key de Cloudinary. |
| `CLOUDINARY_API_SECRET` | vacío | API secret de Cloudinary. |

#### Modos de desarrollo

- **Correos (`dev-outbox`):** sin `RESEND_API_KEY`, los correos no se envían: se guardan como archivos `.html` en la carpeta `outbox/`. El código de verificación del registro está en el archivo más reciente.
- **Imágenes (`dev-local`):** sin credenciales de Cloudinary, las imágenes quedan en disco.
- `GET /health` muestra qué modo está activo.

### 6. Migraciones y Ejecución

Crear las tablas de la base de datos:

```bash
DEBUG=false alembic upgrade head
```

Ejecutar el proyecto:

```bash
uvicorn app.main:app --reload
```

El servicio estará disponible en: <http://localhost:8000>, y la documentación interactiva (Swagger) en: <http://localhost:8000/docs>.

Con `SEED_ON_STARTUP=true`, los datos de prueba se cargan solos al arrancar. Para cargarlos a mano:

```bash
DEBUG=false python -m app.seeders.run
```

El seeder es idempotente: se puede ejecutar varias veces sin duplicar datos. Para empezar desde cero, detén el servidor, borra `gamevault.db` y repite `alembic upgrade head`.

> En PowerShell, `DEBUG=false comando` no funciona. Usa `$env:DEBUG="false"; alembic upgrade head`, o deja `DEBUG=false` en tu `.env`.

Después de cambiar un modelo:
