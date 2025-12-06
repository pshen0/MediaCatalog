# Media Catalog

Студенческий проект HSE SecDev 2025: каталог фильмов и курсов «к просмотру» с REST API.
![CI](https://github.com/pshen0/MediaCatalog/actions/workflows/ci.yml/badge.svg)


## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
pre-commit install --hook-type pre-push
uvicorn app.main:app --reload
```

## Ритуал перед PR
```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроены следующие workflows (GitHub Actions):

- **CI/CD** (`ci.yml`) — тесты и линтинг, required check для `main`
- **Security - SBOM & SCA** (`ci-sbom-sca.yml`) — автоматическая генерация SBOM и сканирование уязвимостей зависимостей

Артефакты безопасности доступны в `EVIDENCE/P09/` и через GitHub Actions artifacts. См. `EVIDENCE/P09/README.md` для подробностей.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Модели
Media
| Поле     | Тип                                  | Описание                       |
| -------- | ------------------------------------ | ------------------------------ |
| id       | str                                  | Уникальный идентификатор       |
| title    | str                                  | Название фильма/курса          |
| kind     | "movie"/"course".                    | Тип записи                     |
| year     | int                                  | Год выпуска (1900 – текущий+1) |
| status   | "planned"/"watching"/"completed"     | Статус просмотра               |
| owner_id | str                                  | ID владельца записи            |

User
| Поле     | Тип | Описание         |
| -------- | --- | ---------------- |
| id       | str | Уникальный ID    |
| username | str | Имя пользователя |


## Эндпойнты
/health
GET /health -> {"status": "ok"}

/media

### POST /media/ - создание новой записи.
Пример:
```bash
  curl -X POST "http://127.0.0.1:8000/media/" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 123" \
  -d '{"title":"Inception","kind":"movie","year":2010,"status":"planned"}'
```

### GET /media/?kind=movie&status=planned - список записей пользователя с фильтрацией по kind и status.
Пример:
```bash
  curl -H "X-User-Id: 123" "http://127.0.0.1:8000/media/"
```

### GET /media/{id} - получение конкретной записи.
Пример:
```bash
  curl -H "X-User-Id: 123" "http://127.0.0.1:8000/media/<id>"
```

### PUT /media/{id} - обновление записи.
Пример:
```bash
  curl -X PUT "http://127.0.0.1:8000/media/<id>" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 123" \
  -d '{"status":"completed"}'
```

### DELETE /media/{id} - даление записи.
Пример:
```bash
  curl -X DELETE "http://127.0.0.1:8000/media/<id>" \
  -H "X-User-Id: 123"
```

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```
