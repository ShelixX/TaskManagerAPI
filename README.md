# TaskManager API

[Русский](#русский) | [English](#english)

## Русский

Асинхронный REST API для управления задачами. В проекте есть регистрация пользователей, JWT access tokens, refresh token rotation через `HttpOnly` cookie и CRUD для задач текущего пользователя.

### Возможности

- регистрация и вход пользователя;
- выдача `access_token` и `refresh_token`;
- хранение refresh token в `HttpOnly` cookie;
- обновление пары токенов через `/auth/refresh`;
- защита от повторного использования refresh token;
- logout с отзывом refresh token;
- CRUD задач для текущего пользователя;
- изоляция задач между пользователями;
- асинхронная работа с БД через SQLAlchemy `AsyncSession`;
- миграции через Alembic;
- тесты для авторизации, токенов и задач.

### Стек

- Python
- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL
- Pydantic
- PyJWT
- pwdlib / Argon2
- pytest
- Docker Compose

### Структура проекта

```text
app/
  main.py                 # точка входа FastAPI-приложения
  config.py               # настройки из .env
  database.py             # async engine и async session factory
  dependencies.py         # зависимости FastAPI
  security.py             # пароли, JWT, refresh token rotation
  bearer.py               # проверка Bearer access token
  models/                 # SQLAlchemy-модели
  schemas/                # Pydantic-схемы
  repositories/           # слой доступа к данным
  services/               # бизнес-логика
  routers/                # API-роуты
alembic/                  # миграции базы данных
tests/                    # тесты
docker-compose.yml        # PostgreSQL для локальной разработки
requirements.txt          # зависимости Python
```

### Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=change-me-to-a-long-random-secret
DATABASE_URL=postgresql+asyncpg://username:password123@localhost:5432/taskmanager
SYNC_DATABASE_URL=postgresql+psycopg://username:password123@localhost:5432/taskmanager
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

`DATABASE_URL` используется приложением через `create_async_engine`.

`SYNC_DATABASE_URL` используется Alembic, потому что миграции в проекте запускаются через синхронный engine.

Для локального запуска без HTTPS оставьте `COOKIE_SECURE=false`, иначе браузер не будет отправлять secure cookie по HTTP.

### Установка и запуск

Создайте и активируйте виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установите зависимости:

```powershell
python -m pip install -r requirements.txt
```

Запустите PostgreSQL:

```powershell
docker compose up -d
```

Примените миграции:

```powershell
python -m alembic upgrade head
```

Запустите API:

```powershell
python -m uvicorn app.main:app --reload
```

После запуска:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API

#### Auth

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/auth/register` | регистрация пользователя |
| `POST` | `/auth/login` | вход, выдача access token и установка refresh cookie |
| `POST` | `/auth/refresh` | обновление access/refresh token |
| `POST` | `/auth/logout` | выход и отзыв refresh token |
| `GET` | `/auth/me` | профиль текущего пользователя |

Пример регистрации:

```powershell
curl -X POST http://127.0.0.1:8000/auth/register `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

Пример входа:

```powershell
curl -X POST http://127.0.0.1:8000/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=testuser&password=password123"
```

Ответ содержит `access_token`. Для защищенных эндпоинтов передавайте его в заголовке:

```text
Authorization: Bearer <access_token>
```

Refresh token хранится в cookie `refresh_token` с путем `/auth`.

#### Tasks

Все эндпоинты `/tasks` требуют Bearer access token.

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/tasks/` | создать задачу |
| `GET` | `/tasks/` | получить список своих задач |
| `GET` | `/tasks/{task_id}` | получить задачу по ID |
| `PATCH` | `/tasks/{task_id}` | частично обновить задачу |
| `DELETE` | `/tasks/{task_id}` | удалить задачу |

Пример создания задачи:

```powershell
curl -X POST http://127.0.0.1:8000/tasks/ `
  -H "Authorization: Bearer <access_token>" `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Write README\",\"description\":\"Document project setup\"}"
```

Пример обновления задачи:

```powershell
curl -X PATCH http://127.0.0.1:8000/tasks/1 `
  -H "Authorization: Bearer <access_token>" `
  -H "Content-Type: application/json" `
  -d "{\"is_completed\":true}"
```

### Модели данных

#### User

- `id`
- `username`
- `password`
- `is_active`
- `created_at`

#### Task

- `id`
- `title`
- `description`
- `is_completed`
- `created_at`
- `user_id`

#### RefreshToken

- `id`
- `jti`
- `token`
- `created_at`
- `expires_at`
- `revoked`
- `user_id`

### Тесты

Запуск тестов:

```powershell
python -m pytest -q
```

Тесты переопределяют зависимость `get_db` и используют асинхронную SQLite-базу через `sqlite+aiosqlite://`, поэтому локальный PostgreSQL для тестов не нужен.

### Миграции

Создать новую миграцию после изменения моделей:

```powershell
python -m alembic revision --autogenerate -m "describe changes"
```

Применить миграции:

```powershell
python -m alembic upgrade head
```

Откатить последнюю миграцию:

```powershell
python -m alembic downgrade -1
```

## English

Asynchronous REST API for task management. The project includes user registration, JWT access tokens, refresh token rotation via an `HttpOnly` cookie, and CRUD operations for the current user's tasks.

### Features

- user registration and login;
- issuing `access_token` and `refresh_token`;
- storing refresh token in an `HttpOnly` cookie;
- refreshing the token pair through `/auth/refresh`;
- protection against refresh token reuse;
- logout with refresh token revocation;
- CRUD operations for the current user's tasks;
- task isolation between users;
- asynchronous database access through SQLAlchemy `AsyncSession`;
- database migrations with Alembic;
- tests for authentication, tokens, and tasks.

### Tech Stack

- Python
- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL
- Pydantic
- PyJWT
- pwdlib / Argon2
- pytest
- Docker Compose

### Project Structure

```text
app/
  main.py                 # FastAPI application entry point
  config.py               # settings loaded from .env
  database.py             # async engine and async session factory
  dependencies.py         # FastAPI dependencies
  security.py             # passwords, JWT, refresh token rotation
  bearer.py               # Bearer access token validation
  models/                 # SQLAlchemy models
  schemas/                # Pydantic schemas
  repositories/           # data access layer
  services/               # business logic
  routers/                # API routes
alembic/                  # database migrations
tests/                    # tests
docker-compose.yml        # PostgreSQL for local development
requirements.txt          # Python dependencies
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=change-me-to-a-long-random-secret
DATABASE_URL=postgresql+asyncpg://username:password123@localhost:5432/taskmanager
SYNC_DATABASE_URL=postgresql+psycopg://username:password123@localhost:5432/taskmanager
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

`DATABASE_URL` is used by the application through `create_async_engine`.

`SYNC_DATABASE_URL` is used by Alembic because migrations in this project run through a synchronous engine.

For local development without HTTPS, keep `COOKIE_SECURE=false`; otherwise, the browser will not send secure cookies over HTTP.

### Installation And Run

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start PostgreSQL:

```powershell
docker compose up -d
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

Run the API:

```powershell
python -m uvicorn app.main:app --reload
```

After startup:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### API

#### Auth

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | register a user |
| `POST` | `/auth/login` | log in, issue an access token, and set refresh cookie |
| `POST` | `/auth/refresh` | refresh access/refresh token |
| `POST` | `/auth/logout` | log out and revoke refresh token |
| `GET` | `/auth/me` | current user profile |

Registration example:

```powershell
curl -X POST http://127.0.0.1:8000/auth/register `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

Login example:

```powershell
curl -X POST http://127.0.0.1:8000/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=testuser&password=password123"
```

The response contains `access_token`. Send it in the header for protected endpoints:

```text
Authorization: Bearer <access_token>
```

The refresh token is stored in the `refresh_token` cookie with the `/auth` path.

#### Tasks

All `/tasks` endpoints require a Bearer access token.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/tasks/` | create a task |
| `GET` | `/tasks/` | get the current user's tasks |
| `GET` | `/tasks/{task_id}` | get a task by ID |
| `PATCH` | `/tasks/{task_id}` | partially update a task |
| `DELETE` | `/tasks/{task_id}` | delete a task |

Create task example:

```powershell
curl -X POST http://127.0.0.1:8000/tasks/ `
  -H "Authorization: Bearer <access_token>" `
  -H "Content-Type: application/json" `
  -d "{\"title\":\"Write README\",\"description\":\"Document project setup\"}"
```

Update task example:

```powershell
curl -X PATCH http://127.0.0.1:8000/tasks/1 `
  -H "Authorization: Bearer <access_token>" `
  -H "Content-Type: application/json" `
  -d "{\"is_completed\":true}"
```

### Data Models

#### User

- `id`
- `username`
- `password`
- `is_active`
- `created_at`

#### Task

- `id`
- `title`
- `description`
- `is_completed`
- `created_at`
- `user_id`

#### RefreshToken

- `id`
- `jti`
- `token`
- `created_at`
- `expires_at`
- `revoked`
- `user_id`

### Tests

Run tests:

```powershell
python -m pytest -q
```

Tests override the `get_db` dependency and use an asynchronous SQLite database through `sqlite+aiosqlite://`, so local PostgreSQL is not required for tests.

### Migrations

Create a new migration after changing models:

```powershell
python -m alembic revision --autogenerate -m "describe changes"
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

Roll back the latest migration:

```powershell
python -m alembic downgrade -1
```
