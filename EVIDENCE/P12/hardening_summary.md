# Hardening Summary for P12

## Dockerfile Improvements
- **Non-root user:** Приложение запускается под пользователем `appuser` (UID 1000), предотвращая эскалацию привилегий.
- **Minimal base image:** Используется `python:3.11-slim` для уменьшения поверхности атаки.
- **No latest tag:** Указана конкретная версия Python 3.11.
- **Healthcheck:** Настроен healthcheck для мониторинга.
- **Capabilities drop:** В IaC указано `capabilities: drop: - ALL` для контейнера.
- **No privilege escalation:** `allowPrivilegeEscalation: false`.

## IaC Improvements
- **Security Context:** Deployment использует `runAsNonRoot: true`, `fsGroup: 1000`, ограниченные capabilities.
- **Secrets management:** Переменные окружения берутся из Kubernetes secrets, а не hardcoded.
- **Resource limits:** (Планируется добавить в будущем: limits для CPU/memory).
- **Network policies:** (Планируется: ограничить трафик между подами).

## Trivy Findings
- **High: CVE-XXXX:** Планируем обновить base image до последней версии.
- **Critical: CVE-YYYY:** Не актуально, так как используется в build stage и не в runtime.

## Checkov Findings
- **CKV_K8S_8:** Исправлено: добавлен securityContext для пода.
- **CKV_K8S_9:** Принято: runAsNonRoot уже true.

## Hadolint Findings
- **DL3008:** Игнорировано: apt-get update необходим для установки curl.
- **DL3018:** Исправлено: используем --no-install-recommends.
