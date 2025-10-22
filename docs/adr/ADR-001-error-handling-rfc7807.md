# ADR-001: RFC 7807 и маскирование ошибок
Дата: 2025-09-22
Статус: Accepted

## Context

В текущем сервисе Media Catalog (FastAPI) ошибки возвращаются через HTTPException(detail=...), что может раскрывать внутренние детали (stack trace, SQL-ошибки, пути к файлам и т. п.).
Это нарушает NFR-03 (Обработка ошибок и безопасность информации) и создаёт риск R2 (утечка деталей ошибок), зафиксированный в Threat Model (P04).

Для соответствия принципам безопасного кодирования требуется единый формат ошибок в виде RFC 7807 (Problem Details for HTTP APIs). Также нужно добавить correlation_id для трассировки запроса в логах и CI.

### Alternatives
| Альтернатива | Плюсы | Минусы |
| ------------ | ----- | ------ |
| **1. Возврат FastAPI HTTPException(detail=...)** | Простая реализация, встроено | Раскрывает внутренние детали; не соответствует RFC7807 |
| **2. Использовать библиотеку fastapi-problems**  | Готовый RFC7807 middleware | Внешняя зависимость, меньше контроля над структурой    |
| **3. Собственная реализация (выбрана)** | Гибкость, контроль формата, минимальные зависимости | Требует поддержки и тестирования |

Компромисс: выбрана реализация через утилиту и middleware — меньше зависимостей, но потребует ручного обновления при изменении формата.

## Decision
Добавить универсальный обработчик ошибок (middleware или util) с JSON-ответом:
```
from starlette.responses import JSONResponse
from uuid import uuid4

def problem(status: int, title: str, detail: str):
    cid = str(uuid4())
    payload = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": cid,
    }
    return JSONResponse(payload, status_code=status)

```

## Rollout Plan / Definition of Done

- Добавить problem() в src/core/.
- Обновить тесты API, ожидая RFC7807 JSON-ответ.
- Проверить наличие correlation_id в логах (loguru middleware).
- Включить флаг SECURE_ERRORS=True в dev окружении.
Definition of Done:
- Все ошибки (в т.ч. валидационные) возвращаются в RFC7807 формате.
- Каждая ошибка содержит correlation_id.
- Нет утечек внутренних сообщений в ответах.
- Все тесты проходят.
- CI зелёный.

## Consequences
Положительные эффекты:

- Единый формат ошибок для всех компонентов (API, сервис, тесты).
- Исключение утечки внутренней информации (SQL, Python traceback).
- Возможность трассировки инцидентов через correlation_id.

Негативные эффекты:

- Незначительное снижение DX (нужно создавать ошибки через problem()).
- Увеличение накладных расходов на сериализацию JSON.

Связь с Threat Model / NFR:
- NFR-03, NFR-08;
- R4, R8;

## Links
- NFR-03, NFR-08;
- R4, R8, F4
- middleware.py, rfc7807_handler.py, main.py
- tests/test_errors.py::test_internal_error_rfc7807

### Изменения по этому ADR находятся в коммите - ADR & Tests: Implement ADR-001 RFC7807 error handling and correlation_id - 4b8eac029b89323806f7a11dd7e024038026841e
