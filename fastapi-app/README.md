# FastAPI Application

FastAPI приложение, развернутое в Docker контейнере.

## Описание

FastAPI приложение с модульной архитектурой, включающее:
- **Core**: Конфигурация и настройки базы данных
- **Routers**: API endpoints для работы с данными
- **Schemas**: Pydantic схемы для валидации данных
- **Services**: Бизнес-логика приложения

## Быстрый старт

### Установка и запуск

```bash
# Перейдите в директорию проекта
cd /opt/fastapi-app

# Запустите скрипт настройки (установит Docker, соберет и запустит приложение)
bash server-setup.sh

# Или вручную:
docker compose build
docker compose up -d
```

### Проверка работы

```bash
# Проверка статуса
docker compose ps

# Проверка логов
docker compose logs -f

# Проверка health endpoint
curl http://localhost:8002/health
```

## Доступ к приложению

- **API**: `http://89.111.155.164:8002`
- **Health Check**: `http://89.111.155.164:8002/health`
- **API Документация (Swagger)**: `http://89.111.155.164:8002/docs`
- **Альтернативная документация (ReDoc)**: `http://89.111.155.164:8002/redoc`

## API Endpoints

### `GET /`
Корневой endpoint, возвращает приветственное сообщение.

**Пример запроса:**
```bash
curl http://localhost:8002/
```

**Ответ:**
```json
{
  "message": "Welcome to FastAPI Application",
  "version": "1.0.0"
}
```

### `GET /health`
Health check endpoint для мониторинга состояния приложения.

**Пример запроса:**
```bash
curl http://localhost:8002/health
```

**Ответ:**
```json
{
  "status": "healthy"
}
```

### `GET /api/v1/items/{item_id}`
Получение информации о конкретном item по ID.

**Пример запроса:**
```bash
curl http://localhost:8002/api/v1/items/1
```

**Ответ (если item найден):**
```json
{
  "id": 1,
  "name": "Item name",
  "description": "Item description"
}
```

**Ответ (если item не найден):**
```json
{
  "detail": "Item with id 1 not found"
}
```

### Другие endpoints

Полный список доступных endpoints можно посмотреть в интерактивной документации Swagger UI: `http://89.111.155.164:8002/docs`

## Управление контейнером

### Полезные команды

```bash
# Перейти в директорию проекта
cd /opt/fastapi-app

# Просмотр статуса
docker compose ps

# Просмотр логов
docker compose logs -f

# Просмотр последних 50 строк логов
docker compose logs --tail=50

# Перезапуск приложения
docker compose restart

# Остановка приложения
docker compose down

# Остановка и удаление volumes
docker compose down -v

# Пересборка образа (после изменений в коде)
docker compose build --no-cache
docker compose up -d

# Просмотр использования ресурсов
docker stats fastapi-app
```

## Структура проекта

```
/opt/fastapi-app/
├── app/                    # Основная директория приложения
│   ├── __init__.py
│   ├── main.py            # Главный файл приложения (точка входа)
│   ├── core/              # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py      # Конфигурация приложения
│   │   └── database.py    # Настройки базы данных
│   ├── routers/           # API роутеры
│   │   ├── __init__.py
│   │   └── items.py       # Роутер для работы с items
│   ├── schemas/           # Pydantic схемы
│   │   ├── __init__.py
│   │   └── items.py       # Схемы для items
│   └── services/          # Бизнес-логика
│       ├── __init__.py
│       └── items_service.py  # Сервис для работы с items
├── main.py                # Старый файл (legacy, не используется)
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
├── server-setup.sh        # Скрипт автоматической настройки
└── README.md             # Документация (этот файл)
```

## Технические детали

### Зависимости

- `fastapi==0.104.1` - веб-фреймворк
- `uvicorn[standard]==0.24.0` - ASGI сервер
- `python-dotenv==1.0.0` - загрузка переменных окружения
- `pydantic>=2.12.4` - валидация данных
- `pydantic-settings==2.1.0` - настройки приложения

### Docker

- **Базовый образ**: `python:3.11-slim`
- **Порт**: `8002`
- **Переменные окружения**: `PORT=8002`
- **Health check**: проверка каждые 30 секунд

### Решение проблем

#### Проблема: Ошибка при сборке образа (gcc)

**Проблема:** При сборке Docker образа возникала ошибка установки `gcc` из-за проблем с сетью/репозиториями Debian.

**Решение:** `gcc` был удален из Dockerfile, так как он не требуется для данного приложения. Все зависимости в `requirements.txt` - это чистые Python пакеты, которые устанавливаются из бинарных wheel файлов и не требуют компиляции.

#### Проблема: Порт уже занят

Если порт 8002 уже занят, измените его в `docker-compose.yml`:

```yaml
ports:
  - "8003:8002"  # Внешний порт:внутренний порт
```

И обновите переменную окружения:
```yaml
environment:
  - PORT=8002
```

## Переменные окружения

Приложение использует файл `.env` для переменных окружения (если он существует).

Создайте файл `.env` в директории проекта:

```bash
PORT=8002
# Добавьте другие переменные по необходимости
```

## Мониторинг

### Health Check

Приложение имеет встроенный health check endpoint, который проверяется Docker:

```bash
# Проверка вручную
curl http://localhost:8002/health
```

### Логи

```bash
# Просмотр логов в реальном времени
docker compose logs -f fastapi-app

# Поиск ошибок в логах
docker compose logs fastapi-app | grep -i error
```

## Разработка

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения (используется app/main.py)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Обновление кода

```bash
# После изменений в коде:
cd /opt/fastapi-app
docker compose build --no-cache
docker compose up -d
```

## Безопасность

⚠️ **Важно для продакшена:**

1. Измените CORS настройки в `main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]  # Вместо ["*"]
   ```

2. Используйте HTTPS (настройте reverse proxy, например nginx)

3. Добавьте аутентификацию для защищенных endpoints

4. Используйте переменные окружения для секретов (не храните в коде)

## Поддержка

При возникновении проблем:

1. Проверьте логи: `docker compose logs -f`
2. Проверьте статус: `docker compose ps`
3. Проверьте порт: `netstat -tlnp | grep 8002`
4. Перезапустите: `docker compose restart`

## Полезные ссылки

- [FastAPI документация](https://fastapi.tiangolo.com/)
- [Uvicorn документация](https://www.uvicorn.org/)
- [Docker Compose документация](https://docs.docker.com/compose/)

