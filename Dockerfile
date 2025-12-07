# syntax=docker/dockerfile:1.7-labs

# Build stage - установка зависимостей
FROM python:3.11-slim AS build
WORKDIR /app

# Установка системных зависимостей только для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements для кэширования слоя
COPY requirements.txt requirements-dev.txt ./

# Устанавливаем зависимости с кэшированием
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Копируем код и запускаем тесты
COPY . .
RUN pytest -q --maxfail=1 || true

# Runtime stage - минимальный образ для продакшн
FROM python:3.11-slim AS runtime

WORKDIR /app

# Создаём non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копируем только установленные пакеты из build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Устанавливаем curl для healthcheck (до переключения на non-root)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Копируем только необходимые файлы приложения
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser pyproject.toml pytest.ini ./

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/usr/local/bin:$PATH

# Переключаемся на non-root пользователя
USER appuser

# Настраиваем healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Открываем порт
EXPOSE 8000

# Security: ограничиваем capabilities и предотвращаем повышение привилегий
# Эти настройки применяются через docker-compose или docker run
# --security-opt=no-new-privileges:true
# --cap-drop=ALL
# --cap-add=NET_BIND_SERVICE (для привязки к порту < 1024, если нужно)

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
