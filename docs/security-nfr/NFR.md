# Таблица требований безопасности для Media Catalog

| ID     | Название           | Описание             | Метрика / Порог | Проверка          | Компонент | Приоритет |
| ------ | ------------------ | -------------------- | ----------------| ----------------- | --------- | --------- |
| NFR-01 | Аутентификация     | Все запросы к защищённым эндпоинтам должны быть аутентифицированы  | 100% запросов к media требуют валидного идентификатора пользователя | Unit/integration тесты + CI (security_scan) | api/auth | High |
| NFR-02 | Собственность | Запись по id доступна только владельцу | 0% случаев получения чужих записей | Unit тесты | api/media | High |
| NFR-03 | Валидация входа | Все JSON payload'ы проходят валидацию | 100% некорректных payload → 4xx | Unit тесты | api/validation | High |
| NFR-04 | Управление зависимостями (SCA) | Критичные/High уязвимости устраняются в срок | Critical/High исправить ≤ 7 дней| CI reports (pip-audit/safety) + Issues | build/ci | High |
| NFR-05 | SAST | Статический анализ кода на security lows | Semgrep/Bandit: 0 запретов на High | CI semgrep/bandit reports | ci, src | High |
| NFR-06 | Секреты в репозитории | Запрещено хранение секретов в репозитории | 0 секретов в git history | pre-commit detect-secrets + periodic scan | repo | High |
| NFR-07 | TTL токенов/сессий | Время жизни токена ограничено | JWT token ttl ≤ 1h; refresh ttl ≤ 30d | env + unit тесты | auth | Medium |
| NFR-08 | Логи и маскирование PII | Логи не содержат необработанные PII; лог содержит correlation_id | 100% запросов логируются с request_id; PII маскируется в 100% случаев  | Лог-ревью + unit tests | logging | Medium |
| NFR-09 | Шифрование чувствительных данных | Чувствительные поля хранятся зашифрованными | sensitive_fields_encrypted = true | Unit-тесты | storage | Medium |
| NFR-10 | Производительность (NFR для Security) | p95 времени ответа для media endpoints в пределах допустимого значения | p95 ≤ 300 ms | Нагрузочный тест | api/perf | Medium |
| NFR-11 | Rate limiting | Защита от DDoS/перебора | Per-user limit: 120 req/min | Интеграционные тесты + мониторинг | edge/api | Medium |
