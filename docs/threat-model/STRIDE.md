# STRIDE Threat Model — Media Catalog

| Поток/Элемент | Угроза (STRIDE) | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|-----------------|------------------|---------|-----------|--------------|----------------------|
| F1 (X-User-Id Header) | **Spoofing** | Подмена идентификатора пользователя | Проверка формата и наличия заголовка | #7 | Unit tests `test_auth_header` |
| F1 / F8 | **Information Disclosure** | Перехват трафика | HTTPS, HSTS в конфиге | #15 | curl/TLS scan |
| F3 (JSON payload) | **Tampering** | Изменение структуры входных данных | Валидация через Pydantic | #9 | Unit tests |
| F4 (Query params) | **Repudiation** | Пользователь отрицает действия | Логирование и correlation_id | #14 | Просмотр логов |
| F5 (DB операции) | **Tampering** | Изменение чужих данных | Проверка `owner_id` | #8 | e2e Forbidden test |
| SVC (Service Layer) | **Elevation of Privilege** | Обход проверки владельца | Централизованный guard | #8 | code review, tests |
| API Gateway | **DoS** | Перегрузка запросами | Rate limit 120 req/min | #17 | Интеграционный тест |
| DB | **Information Disclosure** | Утечка PII через логи | Маскирование, фильтр логов | #14 | Линтер логов |
| CI/CD | **Tampering** | Уязвимости в коде | Semgrep/Bandit | #11 | CI отчёт |
| Repo | **Information Disclosure** | Секреты в git | detect-secrets | #12 | pre-commit лог |
| F6 (DB → SVC) | **Tampering** | Подмена данных из хранилища | Read-only режим на GET | #13 | Unit test read-only |
| A1 (Middleware) | **Denial of Service** | Циклическая проверка хедеров | Request timeout 3s | #17 | Integration test |
