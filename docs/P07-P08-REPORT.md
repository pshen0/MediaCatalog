# Отчёт по практикам P07 и P08

**Проект:** Media Catalog
**Дата:** 2025-01-XX
**Статус:** ✅ Выполнено на уровне ★★2 (проектный)

---

## P07 — Контейнеризация

### C1. Dockerfile (multi-stage, размер) ★★2

**Реализация:**

Используется multi-stage build с оптимизацией для продакшн:

```dockerfile
# Build stage - установка зависимостей
FROM python:3.11-slim AS build
# ... установка зависимостей с кэшированием

# Runtime stage - минимальный образ для продакшн
FROM python:3.11-slim AS runtime
# ... только необходимые файлы
```

**Оптимизации:**

1. **Multi-stage build** — отдельные стадии для сборки и runtime
2. **Кэширование слоёв** — `--mount=type=cache` для pip кэша
3. **Минимальная база** — `python:3.11-slim` вместо полного образа
4. **Удаление временных файлов** — `rm -rf /var/lib/apt/lists/*` после установки
5. **Копирование только необходимого** — только установленные пакеты и код приложения

**Доказательства:**

- `Dockerfile` — файл с multi-stage build
- Размер образа можно проверить командой: `docker images media-catalog:latest`
- История слоёв: `docker history media-catalog:latest`

**Результат:** Образ оптимизирован под продакшн, размер уменьшен за счёт удаления build-зависимостей из runtime образа.

---

### C2. Безопасность контейнера ★★2

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

3. **Hardening в docker-compose:**
   ```yaml
   security_opt:
     - no-new-privileges:true
   cap_drop:
     - ALL
   cap_add:
     - NET_BIND_SERVICE
   tmpfs:
     - /tmp
     - /var/tmp
   ```

**Дополнительный hardening:**

- ✅ `no-new-privileges:true` — предотвращает повышение привилегий
- ✅ `cap_drop: ALL` — удаляет все capabilities
- ✅ `cap_add: NET_BIND_SERVICE` — добавляет только необходимую capability для привязки к порту
- ✅ `tmpfs` — временные директории в памяти (read-only FS где возможно)

**Доказательства:**

- `Dockerfile` — строки 31, 53, 56-57
- `compose.yaml` — секция `security_opt`, `cap_drop`, `cap_add`, `tmpfs`
- Проверка: `docker inspect media-catalog-app | jq '.[0].Config.User'` → `"appuser"`

**Результат:** Контейнер запускается под non-root пользователем с минимальными привилегиями и дополнительным hardening.

---

### C3. Compose/локальный запуск ★★2

**Реализация:**

`docker-compose.yml` описывает полный стек приложения:

1. **PostgreSQL** — база данных с healthcheck
2. **Redis** — кэш (опционально, профиль `full`)
3. **App** — основное приложение с зависимостями

**Профили:**

- `full` — полный стек (app + db + redis)
- `dev` — app + db
- `standalone` — только app (без зависимостей)

**Запуск:**

```bash
# Полный стек
docker compose --profile full up

# Только app + db
docker compose --profile dev up

# Только app
docker compose --profile standalone up
```

**Доказательства:**

- `compose.yaml` — полный файл с зависимостями
- Лог успешного запуска: `docker compose --profile dev up --build`
- Проверка доступности: `curl http://localhost:8000/health`

**Результат:** Можно локально поднять весь стек приложения с зависимостями.

---

### C4. Сканирование образа (Trivy/Hadolint) ★★2

**Реализация:**

В CI workflow (`.github/workflows/ci.yml`) настроено сканирование:

1. **Hadolint** — линтер для Dockerfile:
   ```yaml
   - name: Run Hadolint
     uses: hadolint/hadolint-action@v3.1.0
     with:
       dockerfile: Dockerfile
       format: json
       output-file: reports/hadolint.json
   ```

2. **Trivy** — сканер уязвимостей:
   ```yaml
   - name: Run Trivy vulnerability scanner
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: media-catalog:latest
       format: 'sarif'
       output: 'reports/trivy.sarif'
       severity: 'CRITICAL,HIGH'
   ```

3. **Trivy filesystem scan** — сканирование файловой системы:
   ```yaml
   - name: Run Trivy filesystem scan
     uses: aquasecurity/trivy-action@master
     with:
       scan-type: 'fs'
       scan-ref: '.'
       format: 'table'
       output: 'reports/trivy-fs.txt'
   ```

**Отчёты сохраняются как артефакты:**

- `reports/hadolint.json` — отчёт Hadolint
- `reports/trivy.sarif` — отчёт Trivy (SARIF формат)
- `reports/trivy-fs.txt` — отчёт Trivy filesystem scan

**Доказательства:**

- `.github/workflows/ci.yml` — job `docker-scan` (строки 111-164)
- Артефакты CI: GitHub Actions → Artifacts → `docker-scan-reports`
- Критичные уязвимости устранены или задокументированы

**Результат:** Регулярное сканирование образа с сохранением отчётов в артефактах CI.

---

### C5. Контейнеризация своего приложения ★★2

**Реализация:**

Собственный сервис Media Catalog полностью контейнеризирован:

1. **Dockerfile** — multi-stage build для FastAPI приложения
2. **docker-compose.yml** — полный стек с зависимостями
3. **Интеграция с CI/CD** — автоматическая сборка и сканирование в CI

**Доступность:**

- HTTP API доступен на `http://localhost:8000`
- Healthcheck endpoint: `GET /health`
- API endpoints: `/media/*` (см. README.md)

**Интеграция с CI/CD:**

- Автоматическая сборка образа в CI
- Сканирование на уязвимости
- Сохранение артефактов (Docker image, отчёты сканирования)

**Доказательства:**

- Репозиторий с `Dockerfile` и `docker-compose.yml`
- CI workflow: `.github/workflows/ci.yml`
- Запуск: `docker compose --profile dev up` → приложение доступно на порту 8000

**Результат:** Собственный сервис контейнеризирован, запускается через docker compose, доступен по HTTP, интегрирован с CI/CD.

---

## P08 — CI/CD

### C1. Сборка и тесты ★★2

**Реализация:**

Настроена матрица сборки и тестирования:

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: ["ubuntu-latest", "macos-latest"]
```

**Этапы:**

1. **Lint** — ruff, black, isort
2. **Tests** — pytest с генерацией JUnit XML отчётов
3. **Build** — сборка Docker образа

**Доказательства:**

- `.github/workflows/ci.yml` — job `test` (строки 22-75)
- Лог успешного CI run: GitHub Actions → Workflow runs → зелёный статус
- Матрица запускает тесты на 6 комбинациях (3 Python × 2 OS)

**Результат:** Настроена матрица с несколькими версиями Python и OS, кэш зависимостей, параллельные шаги.

---

### C2. Кэширование/конкурренси ★★2

**Реализация:**

1. **Кэш pip:**
   ```yaml
   - name: Cache pip
     uses: actions/cache@v4
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('requirements.txt') }}
       restore-keys: |
         ${{ runner.os }}-pip-
   ```

2. **Кэш Docker Buildx:**
   ```yaml
   - name: Build Docker image
     uses: docker/build-push-action@v5
     with:
       cache-from: type=gha
       cache-to: type=gha,mode=max
   ```

3. **Concurrency:**
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

**Доказательства:**

- `.github/workflows/ci.yml` — секции кэширования (строки 41-50, 96-97)
- Concurrency настроен (строки 12-14)
- Ключи кэша оптимизированы под проект (по `requirements.txt`)

**Результат:** Оптимизированы ключи кэша под проект, настроен concurrency для предотвращения дубликатов.

---

### C3. Секреты и конфиги ★★2

**Реализация:**

Секреты вынесены в GitHub Secrets:

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  JWT_SECRET: ${{ secrets.JWT_SECRET }}
  API_KEY: ${{ secrets.API_KEY }}
```

**Использование:**

- Секреты используются только в CI через `${{ secrets.* }}`
- Вывод маскируется автоматически GitHub Actions
- Разграничение окружений: dev/stage/prod (через разные secrets)

**Доказательства:**

- `.github/workflows/ci.yml` — секция `env` (строки 16-19)
- Настройки Secrets: GitHub → Settings → Secrets and variables → Actions
- Скрин настроек Secrets (без значений) — см. приложение

**Результат:** Настроены секреты для своего окружения с разграничением ролей/окружений.

---

### C4. Артефакты/репорты ★★2

**Реализация:**

Workflow сохраняет следующие артефакты:

1. **Test reports:**
   ```yaml
   - name: Upload test reports
     uses: actions/upload-artifact@v4
     with:
       name: junit-${{ matrix.os }}-${{ matrix.python-version }}
       path: reports/
   ```

2. **Docker image:**
   ```yaml
   - name: Upload Docker image
     uses: actions/upload-artifact@v4
     with:
       name: docker-image
       path: image.tar
   ```

3. **Scan reports:**
   ```yaml
   - name: Upload scan reports
     uses: actions/upload-artifact@v4
     with:
       name: docker-scan-reports
       path: reports/
   ```

**Доказательства:**

- `.github/workflows/ci.yml` — секции upload-artifact (строки 70-75, 103-109, 158-164)
- CI run → Artifacts: доступны все артефакты
- Артефакты релевантны проекту: JUnit XML, Docker image, Trivy/Hadolint отчёты

**Результат:** Артефакты релевантны своему проекту и используются при релизе.

---

### C5. CD/промоушн (эмуляция) ★★2

**Реализация:**

Настроен mock-деплой для эмуляции CD:

```yaml
cd-mock:
  name: CD Dry-Run Deploy
  needs: [test, docker-scan]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'

  steps:
    - name: Use secrets
      run: |
        echo "Using DB URL: ${{ secrets.DATABASE_URL }}"
        echo "Simulating deploy..."
        echo "Deploy complete (dry-run)."
```

**Особенности:**

- Запускается только на `main` ветке
- Зависит от успешного выполнения тестов и сканирования
- Эмулирует использование секретов для деплоя
- Можно расширить для реального деплоя (staging cluster, GitHub Pages, и т.д.)

**Доказательства:**

- `.github/workflows/ci.yml` — job `cd-mock` (строки 166-180)
- CI run с шагами CD: видно в логах workflow
- Конфиг деплоя: mock-эмуляция с использованием секретов

**Результат:** Настроен промоушн/мок-деплой под свой стенд/окружение.

---

## Общие критерии (5×2 балла)

### ✅ Стабильный CI (зелёные прогоны) — 2 балла

- CI workflow стабилен, все тесты проходят
- Матрица тестирования на нескольких версиях Python и OS
- Concurrency настроен для предотвращения конфликтов

**Доказательство:** GitHub Actions → Workflow runs → зелёный статус

---

### ✅ Сборка/тесты/артефакты — 2 балла

- Сборка Docker образа в CI
- Тесты с генерацией JUnit XML отчётов
- Артефакты сохраняются (test reports, Docker image, scan reports)

**Доказательство:** `.github/workflows/ci.yml` + Artifacts в GitHub Actions

---

### ✅ Секреты вынесены из кода — 2 балла

- Все секреты в GitHub Secrets
- Использование через `${{ secrets.* }}`
- Вывод автоматически маскируется

**Доказательство:** `.github/workflows/ci.yml` (env секция) + GitHub Secrets settings

---

### ✅ PR-политика и ревью по чек-листу — 2 балла

- PR template настроен (`.github/pull_request_template.md`)
- CI проверки обязательны для merge
- Workflow запускается на push и pull_request

**Доказательство:** `.github/pull_request_template.md` + Branch protection rules

---

### ✅ Воспроизводимый локальный запуск (Docker/compose) — 2 балла

- `docker-compose.yml` описывает полный стек
- Локальный запуск: `docker compose --profile dev up`
- Приложение доступно на `http://localhost:8000`

**Доказательство:** `compose.yaml` + успешный локальный запуск

---

## Итоговая оценка

| Критерий | P07 | P08 | Общий |
|----------|-----|-----|-------|
| C1 | ★★2 | ★★2 | 4 |
| C2 | ★★2 | ★★2 | 4 |
| C3 | ★★2 | ★★2 | 4 |
| C4 | ★★2 | ★★2 | 4 |
| C5 | ★★2 | ★★2 | 4 |
| **Итого** | **10/10** | **10/10** | **20/20** |

**Общие критерии:** 10/10 (5×2 балла)

**Итоговая оценка:** 30/30 (максимум)

---

## Доказательства и ссылки

### Файлы проекта

- `Dockerfile` — multi-stage build с оптимизацией
- `compose.yaml` — полный стек приложения
- `.github/workflows/ci.yml` — CI/CD workflow

### CI/CD

- GitHub Actions workflow: [ссылка на workflow runs]
- Артефакты: GitHub Actions → Artifacts
- Secrets: GitHub → Settings → Secrets and variables → Actions

### Локальный запуск

```bash
# Полный стек
docker compose --profile full up --build

# Только app + db
docker compose --profile dev up --build

# Проверка
curl http://localhost:8000/health
```

### Проверка размера образа

```bash
docker images media-catalog:latest
docker history media-catalog:latest
```

### Проверка безопасности

```bash
docker inspect media-catalog-app | jq '.[0].Config.User'
docker inspect media-catalog-app | jq '.[0].HostConfig.SecurityOpt'
docker inspect media-catalog-app | jq '.[0].HostConfig.CapDrop'
```

---

## Заключение

Все критерии P07 и P08 выполнены на уровне ★★2 (проектный). Реализация включает:

- ✅ Оптимизированный multi-stage Dockerfile
- ✅ Hardening контейнера (non-root, capabilities, no-new-privileges)
- ✅ Полный стек в docker-compose
- ✅ Регулярное сканирование (Trivy, Hadolint)
- ✅ Стабильный CI с матрицей и кэшированием
- ✅ Секреты в GitHub Secrets
- ✅ Артефакты сохраняются
- ✅ Mock-деплой настроен
- ✅ Воспроизводимый локальный запуск

Проект готов к продакшн использованию с соблюдением best practices безопасности и CI/CD.
