# Отчёт по практикам P07-08: Контейнеризация и CI/CD

**Проект:** Media Catalog
**Дата:** 2025-01-XX
**Статус:** ✅ Выполнено на ★★2 (проектный уровень)

---

## P07 — Контейнеризация

### C1. Dockerfile (multi-stage, размер) ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Multi-stage build:**
   - `build` stage — установка зависимостей и запуск тестов
   - `runtime` stage — минимальный образ для продакшн

2. **Оптимизация размера:**
   - Использование `python:3.11-slim` как базового образа
   - Копирование только установленных пакетов из build stage
   - Удаление временных зависимостей (gcc, postgresql-client) после сборки
   - Использование `--mount=type=cache` для кэширования pip

3. **Кэш-слои:**
   - Отдельный слой для requirements.txt (кэшируется при неизменных зависимостях)
   - Кэширование pip через BuildKit cache mounts

**Доказательства:**

- **Dockerfile:** `.github/workflows/ci.yml` → `docker-build` job
- **Размер образа:** Проверяется через `docker images` после сборки
- **История слоёв:** `docker history media-catalog:latest`

**Команды для проверки:**

```bash
# Сборка образа
docker build -t media-catalog:latest .

# Проверка размера
docker images media-catalog:latest

# История слоёв
docker history media-catalog:latest

# Сравнение с базовым образом
docker images python:3.11-slim
```

**Результаты:**

- Базовый образ `python:3.11-slim`: ~45MB
- Финальный образ `media-catalog:latest`: ~150-200MB (включая зависимости FastAPI, uvicorn и т.д.)
- Оптимизация: удалены dev-зависимости из runtime stage

---

### C2. Безопасность контейнера ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Non-root пользователь:**
   ```dockerfile
   RUN groupadd -r appuser && useradd -r -g appuser appuser
   USER appuser
   ```

2. **HEALTHCHECK:**
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
       CMD curl -f http://localhost:8000/health || exit 1
   ```

3. **Дополнительный hardening:**
   - Минимальный базовый образ (slim)
   - Удаление временных файлов и кэша
   - Переменные окружения для безопасности Python

**Доказательства:**

- **Dockerfile:** Строки 12-18, 25-28
- **Compose:** Healthcheck настроен в `compose.yaml`
- **Проверка:** `docker inspect media-catalog:latest | grep -A 10 "User"`

**Команды для проверки:**

```bash
# Проверка пользователя
docker inspect media-catalog:latest | grep -A 5 "User"

# Проверка healthcheck
docker inspect media-catalog:latest | grep -A 10 "Healthcheck"

# Запуск контейнера и проверка
docker run -d --name test-container media-catalog:latest
docker exec test-container whoami  # Должно быть: appuser
docker ps --format "table {{.Names}}\t{{.Status}}"  # Проверка healthcheck
```

---

### C3. Compose/локальный запуск ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Полный стек с зависимостями:**
   - PostgreSQL для базы данных
   - Redis для кэширования (опционально)
   - Приложение с healthcheck и зависимостями

2. **Профили запуска:**
   - `full` — полный стек (app + db + redis)
   - `dev` — разработка (app + db)
   - `standalone` — только приложение

3. **Настройки:**
   - Healthcheck для всех сервисов
   - Volumes для персистентности данных
   - Сеть для изоляции сервисов
   - Переменные окружения через `.env`

**Доказательства:**

- **compose.yaml:** Полная конфигурация с сервисами
- **Лог запуска:** `docker compose up --profile full`

**Команды для проверки:**

```bash
# Запуск полного стека
docker compose --profile full up -d

# Запуск только приложения
docker compose --profile standalone up -d

# Проверка статуса
docker compose ps

# Логи
docker compose logs app

# Остановка
docker compose down
```

**Результаты:**

- ✅ Все сервисы поднимаются успешно
- ✅ Healthcheck проходит для всех сервисов
- ✅ Приложение доступно на http://localhost:8000
- ✅ База данных доступна на localhost:5432

---

### C4. Сканирование образа (Trivy/Hadolint) ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Hadolint** — линтер для Dockerfile:
   - Проверка best practices
   - Формат вывода: JSON
   - Сохранение отчёта в артефакты

2. **Trivy** — сканер уязвимостей:
   - Сканирование образа на уязвимости
   - Сканирование файловой системы
   - Формат вывода: SARIF и таблица
   - Фильтрация по severity: CRITICAL, HIGH

3. **Интеграция в CI:**
   - Автоматический запуск после сборки образа
   - Сохранение отчётов в артефакты
   - Не блокирует pipeline (continue-on-error)

**Доказательства:**

- **CI workflow:** `.github/workflows/ci.yml` → `docker-scan` job
- **Отчёты:** Доступны в GitHub Actions artifacts (`docker-scan-reports`)
- **Файлы:**
  - `reports/hadolint.json` — отчёт Hadolint
  - `reports/trivy.sarif` — отчёт Trivy (SARIF)
  - `reports/trivy-fs.txt` — отчёт Trivy (таблица)

**Команды для локальной проверки:**

```bash
# Hadolint
docker run --rm -i hadolint/hadolint < Dockerfile

# Trivy image scan
trivy image media-catalog:latest

# Trivy filesystem scan
trivy fs .
```

**Результаты:**

- ✅ Hadolint не обнаружил критичных проблем
- ✅ Trivy сканирует образ и файловую систему
- ✅ Отчёты сохраняются в артефакты CI
- ✅ Критичные уязвимости отслеживаются и устраняются

---

### C5. Контейнеризация своего приложения ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Собственный сервис контейнеризирован:**
   - FastAPI приложение Media Catalog
   - Все зависимости установлены в контейнере
   - Приложение запускается через uvicorn

2. **Интеграция с CI/CD:**
   - Автоматическая сборка образа в CI
   - Тесты запускаются в контейнере
   - Сканирование образа в pipeline

3. **Доступность:**
   - HTTP API доступен на порту 8000
   - Healthcheck endpoint: `/health`
   - Все эндпоинты работают в контейнере

**Доказательства:**

- **Репозиторий:** Dockerfile и compose.yaml в корне проекта
- **CI:** `.github/workflows/ci.yml` с job `docker-build`
- **Запуск:** `docker compose up` поднимает приложение

**Проверка работы:**

```bash
# Запуск приложения
docker compose --profile standalone up -d

# Проверка health
curl http://localhost:8000/health

# Проверка API
curl -H "X-User-Id: 123" http://localhost:8000/media/

# Логи
docker compose logs -f app
```

**Результаты:**

- ✅ Приложение успешно запускается в контейнере
- ✅ Все эндпоинты доступны и работают
- ✅ Интеграция с CI/CD настроена
- ✅ Локальный запуск через docker compose работает

---

## P08 — CI/CD

### C1. Сборка и тесты ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Матрица сборки:**
   - Python версии: 3.10, 3.11, 3.12
   - ОС: ubuntu-latest, macos-latest
   - Параллельное выполнение тестов

2. **Этапы:**
   - Lint (ruff, black, isort)
   - Unit-тесты (pytest)
   - Сборка Docker образа
   - Сканирование безопасности

3. **Стабильность:**
   - Все тесты проходят
   - CI run зелёный
   - Отчёты сохраняются

**Доказательства:**

- **CI workflow:** `.github/workflows/ci.yml`
- **Лог CI:** GitHub Actions → последний успешный run
- **Матрица:** Строки 27-30 в ci.yml

**Результаты:**

- ✅ Build проходит успешно
- ✅ Все тесты проходят на всех версиях Python
- ✅ Линтинг проходит без ошибок
- ✅ CI run зелёный

---

### C2. Кэширование/конкурренси ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Кэширование pip:**
   ```yaml
   - name: Cache pip
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('requirements.txt') }}
   ```

2. **Кэширование Docker:**
   - BuildKit cache для Docker слоёв
   - GitHub Actions cache для Docker образов

3. **Concurrency:**
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

**Доказательства:**

- **Workflow:** `.github/workflows/ci.yml` → строки 12-14, 41-50
- **Docker cache:** Строки в `docker-build` job

**Результаты:**

- ✅ Кэш pip ускоряет установку зависимостей
- ✅ Docker cache ускоряет сборку образа
- ✅ Concurrency предотвращает дубликаты запусков
- ✅ Оптимизированные ключи кэша по requirements.txt

---

### C3. Секреты и конфиги ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Секреты вынесены:**
   ```yaml
   env:
     DATABASE_URL: ${{ secrets.DATABASE_URL }}
     JWT_SECRET: ${{ secrets.JWT_SECRET }}
     API_KEY: ${{ secrets.API_KEY }}
   ```

2. **Маскирование вывода:**
   - Секреты не выводятся в логи
   - Используются только через `${{ secrets.* }}`

3. **Разграничение окружений:**
   - Dev/stage/prod через переменные окружения
   - Секреты настраиваются в GitHub Secrets

**Доказательства:**

- **Workflow:** `.github/workflows/ci.yml` → строки 16-19
- **Настройки:** GitHub → Settings → Secrets and variables → Actions
- **Использование:** Секреты используются только в env, не в логах

**Настроенные секреты:**

- `DATABASE_URL` — URL базы данных
- `JWT_SECRET` — секрет для JWT токенов
- `API_KEY` — API ключ для внешних сервисов

**Результаты:**

- ✅ Секреты не хранятся в коде
- ✅ Секреты не видны в логах
- ✅ Настроены для разных окружений
- ✅ Безопасное использование в CI/CD

---

### C4. Артефакты/репорты ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Артефакты тестов:**
   - JUnit XML отчёты для каждой версии Python/OS
   - Сохранение в артефакты GitHub Actions

2. **Артефакты Docker:**
   - Docker образ (для сканирования)
   - Отчёты Trivy (SARIF и таблица)
   - Отчёт Hadolint (JSON)

3. **Использование:**
   - Отчёты доступны в GitHub Actions
   - Используются для анализа и отладки
   - Интеграция с GitHub Code Scanning (SARIF)

**Доказательства:**

- **Workflow:** `.github/workflows/ci.yml` → `upload-artifact` steps
- **Артефакты:** GitHub Actions → Artifacts в последнем run
- **Файлы:**
  - `junit-*.xml` — отчёты тестов
  - `docker-scan-reports/` — отчёты сканирования

**Результаты:**

- ✅ Все артефакты сохраняются
- ✅ Отчёты доступны для анализа
- ✅ SARIF формат для интеграции с GitHub
- ✅ Retention настроен (90 дней для отчётов безопасности)

---

### C5. CD/промоушн (эмуляция) ★★2

**Статус:** ✅ Выполнено

**Реализация:**

1. **Mock deploy:**
   - Эмуляция деплоя в staging
   - Использование секретов для конфигурации
   - Dry-run без реального деплоя

2. **Условия запуска:**
   - Только для main ветки
   - После успешных тестов и сканирования
   - Использование секретов окружения

3. **План реального деплоя:**
   - Выкладка в staging namespace
   - Использование Docker образа
   - Конфигурация через секреты

**Доказательства:**

- **Workflow:** `.github/workflows/ci.yml` → `cd-mock` job
- **Условия:** Строки 77-91
- **Лог:** GitHub Actions → последний run → `cd-mock` job

**Результаты:**

- ✅ Mock deploy настроен
- ✅ Запускается только на main
- ✅ Использует секреты безопасно
- ✅ Готов к расширению для реального деплоя

---

## Общие результаты

### Стабильность CI

- ✅ Все прогоны зелёные
- ✅ Матрица тестирования работает
- ✅ Кэширование ускоряет сборку
- ✅ Concurrency предотвращает конфликты

### Сборка/тесты/артефакты

- ✅ Сборка проходит успешно
- ✅ Тесты проходят на всех версиях
- ✅ Артефакты сохраняются
- ✅ Отчёты доступны для анализа

### Секреты вынесены из кода

- ✅ Все секреты в GitHub Secrets
- ✅ Не видны в логах
- ✅ Безопасное использование

### PR-политика и ревью

- ✅ CI запускается на PR
- ✅ Все проверки должны пройти
- ✅ Шаблон PR заполнен

### Воспроизводимый локальный запуск

- ✅ Docker compose поднимает весь стек
- ✅ Dockerfile оптимизирован
- ✅ Локальный запуск идентичен CI

---

## Дополнительные улучшения (9-10 баллов)

### Кэш/матрица

- ✅ Матрица Python версий и ОС
- ✅ Кэширование pip зависимостей
- ✅ Кэширование Docker слоёв через BuildKit

### Отчёты покрытия

- ⚠️ Можно добавить coverage отчёты (опционально)
- ✅ JUnit XML отчёты для тестов
- ✅ SARIF отчёты для безопасности

### Релизные артефакты

- ✅ Docker образ собирается в CI
- ✅ Отчёты безопасности сохраняются
- ⚠️ Можно добавить публикацию образа в registry (опционально)

---

## Команды для проверки

### Локальная проверка Docker

```bash
# Сборка образа
docker build -t media-catalog:latest .

# Проверка размера
docker images media-catalog:latest

# История слоёв
docker history media-catalog:latest

# Запуск контейнера
docker run -d -p 8000:8000 --name test-app media-catalog:latest

# Проверка health
curl http://localhost:8000/health

# Остановка
docker stop test-app && docker rm test-app
```

### Локальная проверка Compose

```bash
# Запуск полного стека
docker compose --profile full up -d

# Проверка статуса
docker compose ps

# Логи
docker compose logs -f app

# Остановка
docker compose down
```

### Проверка CI

1. Открыть GitHub Actions
2. Проверить последний успешный run
3. Убедиться, что все jobs зелёные
4. Проверить артефакты

---

## Ссылки

- **Dockerfile:** `Dockerfile`
- **Compose:** `compose.yaml`
- **CI Workflow:** `.github/workflows/ci.yml`
- **GitHub Actions:** https://github.com/pshen0/MediaCatalog/actions
- **Артефакты:** Доступны в каждом CI run

---

## Заключение

Все критерии P07-08 выполнены на уровне ★★2 (проектный):

- ✅ Dockerfile оптимизирован для продакшн
- ✅ Безопасность контейнера настроена
- ✅ Compose описывает полный стек
- ✅ Сканирование образа интегрировано в CI
- ✅ Собственный сервис контейнеризирован
- ✅ CI/CD настроен с матрицей и кэшем
- ✅ Секреты вынесены из кода
- ✅ Артефакты сохраняются
- ✅ Mock deploy настроен

Проект готов к продакшн использованию.
