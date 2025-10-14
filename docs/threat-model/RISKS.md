# Risk Register — Media Catalog Service

| ID | Риск | F/NFR | L | I | Score | Стратегия | Контроль | Владелец | Срок | Критерий закрытия |
|----|-------|--------|---|---|--------|------------|-----------|-----------|------|-------------------|
| R1 | Подмена `X-User-Id` | F1 / NFR-01 | 3 | 5 | 15 | Снизить | Проверка формата | @pshen0 | 2025-11 | Unit tests проходят |
| R2 | Отсутствие HTTPS | F1/F8 / NFR-09 | 1 | 5 | 5 | Избежать | HSTS + HTTPS | @pshen0 | 2025-11 | TLS включён |
| R3 | Некорректный JSON payload | F3 / NFR-03 | 2 | 3 | 6 | Снизить | Pydantic схемы | @pshen0 | 2025-11 | 100% coverage |
| R4 | Отсутствие логов действий | F4 / NFR-08 | 3 | 2 | 6 | Снизить | correlation_id | @pshen0 | 2025-11 | Логи с ID |
| R5 | CRUD чужих записей | F5 / NFR-02 | 3 | 5 | 15 | Снизить | Проверка owner_id | @pshen0 | 2025-11 | 403 Forbidden test |
| R6 | Повышение привилегий | SVC / NFR-02 | 2 | 5 | 10 | Снизить | Guard на уровне сервиса | @pshen0 | 2025-11 | e2e test |
| R7 | DoS через API | Edge / NFR-11 | 3 | 4 | 12 | Снизить | Rate-limit | @pshen0 | 2025-11 | CI test |
| R8 | Утечка PII | DB / NFR-08 | 2 | 3 | 6 | Снизить | Маскирование | @pshen0 | 2025-11 | Лог-ревью |
| R9 | Уязвимости в зависимостях | CI / NFR-05 | 3 | 4 | 12 | Снизить | Semgrep, Bandit | @pshen0 | 2025-11 | 0 high findings |
| R10 | Секреты в git | Repo / NFR-06 | 2 | 5 | 10 | Избежать | detect-secrets | @pshen0 | 2025-11 | 0 утечек |
| R11 | Подмена данных из DB | F6 / NFR-07 | 2 | 3 | 6 | Снизить | Read-only на GET | @pshen0 | 2025-11 | Unit test OK |
| R12 | Цикл в middleware | A1 / NFR-11 | 1 | 4 | 4 | Снизить | Timeout | @pshen0 | 2025-11 | Test timeout passes |
