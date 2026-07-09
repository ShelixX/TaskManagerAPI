# TaskManager API

REST API для управления задачами с регистрацией пользователей, JWT-авторизацией и refresh token rotation.

## Возможности

- регистрация и вход пользователя;
- выдача access token и refresh token;
- хранение refresh token в `HttpOnly` cookie;
- обновление пары токенов через `/auth/refresh`;
- защита от повторного использования refresh token;
- выход из аккаунта с отзывом refresh token;
- CRUD-операции с задачами текущего пользователя;
- изоляция задач между пользователями;
- миграции базы данных через Alembic;
- тесты для авторизации, токенов и задач.

## Стек

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- PyJWT
- Argon2
- Pytest
- Docker Compose

## Структура проекта

```text
app/
  main.py                 # точка входа FastAPI-приложения
  config.py               # настройки из .env
  database.py             # подключение к базе данных
  dependencies.py         # зависимости FastAPI
  security.py             # работа с паролями и JWT
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

## Переменные окружения

Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=change-me-to-a-long-random-secret
DATABASE_URL=postgresql+psycopg://username:password123@localhost:5432/taskmanager
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

Для локального запуска без HTTPS установите `COOKIE_SECURE=false`, иначе браузер не будет отправлять secure cookie по HTTP.

## Установка и запуск

1. Создайте и активируйте виртуальное окружение:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите PostgreSQL:

```bash
docker compose up -d
```

4. Примените миграции:

```bash
alembic upgrade head
```

5. Запустите API:

```bash
uvicorn app.main:app --reload
```

После запуска приложение будет доступно по адресу:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API

### Auth

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/auth/register` | регистрация пользователя |
| `POST` | `/auth/login` | вход, получение access token и установка refresh cookie |
| `POST` | `/auth/refresh` | обновление access/refresh token |
| `POST` | `/auth/logout` | выход и отзыв refresh token |
| `GET` | `/auth/me` | профиль текущего пользователя |

Пример регистрации:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

Пример входа:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Ответ содержит `access_token`. Для защищенных эндпоинтов передавайте его в заголовке:

```text
Authorization: Bearer <access_token>
```

### Tasks

Все эндпоинты `/tasks` требуют Bearer access token.

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/tasks/` | создать задачу |
| `GET` | `/tasks/` | получить список своих задач |
| `GET` | `/tasks/{task_id}` | получить задачу по ID |
| `PATCH` | `/tasks/{task_id}` | частично обновить задачу |
| `DELETE` | `/tasks/{task_id}` | удалить задачу |

Пример создания задачи:

```bash
curl -X POST http://127.0.0.1:8000/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write README","description":"Document project setup"}'
```

Пример обновления задачи:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"is_completed":true}'
```

## Модели данных

### User

- `id`
- `username`
- `password`
- `is_active`
- `created_at`

### Task

- `id`
- `title`
- `description`
- `is_completed`
- `created_at`
- `user_id`

### RefreshToken

- используется для ротации refresh token и обнаружения повторного использования токена.

## Тесты

Запуск тестов:

```bash
pytest
```

Тесты используют SQLite in-memory базу и переопределяют зависимость `get_db`, поэтому локальный PostgreSQL для тестов не требуется.

## Миграции

Создать новую миграцию после изменения моделей:

```bash
alembic revision --autogenerate -m "describe changes"
```

Применить миграции:

```bash
alembic upgrade head
```

Откатить последнюю миграцию:

```bash
alembic downgrade -1
```
