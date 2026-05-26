# profile_service

Профиль пользователя (PostgreSQL). Слушает регистрацию из auth, публикует изменения профиля в Kafka.

## Порт и health

Внутри Docker слушает **8000** (через gateway или внутреннюю сеть).  
Локально: `PORT=8000` (см. `main.py`).

```bash
curl http://localhost:8000/health
```

## API (префикс `/profile`)

| Метод | Путь | Auth | Описание |
|-------|------|------|----------|
| GET | `/profile/{user_id}` | JWT | Свой профиль (`display_name` в ответе) |
| PUT | `/profile/{user_id}` | JWT | Обновление → `profile_service.profile.changed` |
| DELETE | `/profile/{user_id}` | JWT | Удаление → `profile_service.user.deleted` |

## Kafka

| Направление | Топик |
|-------------|--------|
| In | `profile_service.user.registered` |
| Out | `profile_service.profile.changed` |
| Out | `profile_service.user.deleted` |

Константы: `src/kafka_topics.py`.

## База данных

- БД: `profile_db`
- Миграции: `src/migrations/sql/` (yoyo)
- Таблица: `profiles`
- `RUN_DB_MIGRATIONS_ON_STARTUP=true` — миграции при старте

## Переменные окружения

| Переменная | Назначение |
|------------|------------|
| `LOG_LEVEL` | Уровень логов (`INFO`) |
| `DATABASE_URL` | `postgresql+asyncpg://.../profile_db` |
| `MIGRATIONS_DATABASE_URL` | sync DSN для yoyo |
| `REDPANDA_BOOTSTRAP_SERVERS` | Kafka |
| `REDPANDA_CONSUMER_GROUP` | consumer group |
| `KEYCLOAK_*` | Валидация JWT |

## Логи

Формат: `время | уровень | logger | сообщение`.  
Настройка: `src/core/logging.py`, вызов в `main.py` при старте.

**Docker:**

```bash
docker logs profile -f
```

**Что смотреть:**

- `profile_service` — старт, миграции, shutdown
- `src.infrastructure.message_broker.consumer` — события `user.registered`
- `src.application.usecases.profile_service` — публикация в Kafka (через producer)

```bash
docker logs profile 2>&1 | grep -E "Kafka|migration|ERROR"
```

## Запуск

```bash
cd ../infra_faberge && make profile-dev
# или
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Тесты

```bash
uv run pytest -q
```
