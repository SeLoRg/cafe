# Развертывание проекта с использованием Docker Compose

Этот проект включает несколько сервисов, таких как база данных, Elasticsearch, Redis, FastAPI backend и Nginx для проксирования. Для развертывания всех сервисов используется Docker Compose.

## Структура проекта

- `db`: PostgreSQL 16.0
- `elasticsearch`: Elasticsearch 8.6.2
- `redis`: Redis 7.4.2
- `cafe`: Backend на FastAPI
- `nginx`: Nginx для проксирования
- `alembic_service`: Alembic для миграций базы данных

## Требования

- Docker
- Docker Compose

Убедитесь, что на вашей машине установлены Docker и Docker Compose. Вы можете проверить их установку с помощью следующих команд:

```bash
docker --version
docker-compose --version
```

## Инструкции по развертыванию

Если вы еще не клонировали проект, сделайте это с помощью:

```bash
git clone https://github.com/SeLoRg/cafe.git
cd cafe
```

## Сборка и запуск сервисов с помощью Docker Compose

Для сборки и запуска всех сервисов используйте команду:

```bash
docker-compose up --build
```
## Применение миграций для базы данных
После того как сервисы будут запущены, вам нужно выполнить миграции для базы данных с помощью Alembic. Для этого:

Перейдите в контейнер в папку с проектом где находится docker-compose.yaml:

```bash
 docker compose run  alembic_service  alembic revision --autogenerate -m "First migrations"
```
```bash
docker compose run alembic_service  alembic upgrade head
```

## Доступ к приложению
После запуска контейнеров, вы сможете получить доступ к вашему приложению:

Frontend: http://localhost:80
Backend: http://localhost:80/api/
## Остановка сервисов
Для остановки всех сервисов выполните:
```bash
docker-compose down
```
Если вы хотите удалить все контейнеры, тома и сети, используйте:

```bash
docker-compose down -v
```

## Тесты
Тесты до конца не доделаны. Пока они затрагивают только слой сервиса эндпоинта

Для запуска перейдите в папку cafe/backend и запустите:
```bash
pytest tests/
```