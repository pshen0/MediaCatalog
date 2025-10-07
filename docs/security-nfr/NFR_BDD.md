# Приёмка в формате Gherkin для Media Catalog

# Auth: все защищенные эндпоинты требуют валидной авторизации

Scenario: Запрос без заголовка авторизации отклоняется\\
Given сервис поднят на stage\\
When клиент делает GET /media/1 без заголовка X-User-Id\\
Then ответ 401 Unauthorized

# Owner: пользователь не может получить чужую запись

Scenario: Доступ к чужой media-записи запрещён\\
Given запись media с id=10 принадлежит user_id=42\\
And в базе есть user_id=100\\
When user_id=100 делает GET /media/10 с валидным заголовком\\
Then ответ 403 Forbidden

# Dependency management: CI падает при critical/high уязвимостях

Scenario: CI обнаружил критическую уязвимость в dependencies\\
Given requirements.txt содержит пакет с known critical CVE\\
When запускается job security_scan в CI\\
Then job завершился с non-zero exit и артефакт audit.json содержит уязвимость уровня CRITICAL or HIGH

# Input validation: некорректный payload возвращает 4xx

Scenario: Неправильный payload на создание записи\\
Given пользователь авторизован\\
When он делает POST /media/ с body {"title":"", "year": 99999}\\
Then ответ 422 Unprocessable Entity и тело ошибки содержит информацию по полям

# Rate limiting: защита от перебора

Scenario: Превышение лимита возвращает 429\\
Given для user_id=123 установлен лимит 120 req/min\\
When клиент делает >120 запросов за минуту к /media\\
Then некоторые ответы содержат 429 Too Many Requests

# Negative: логирование не должно содержать PII

Scenario: Логи не содержат незащищённую PII\\
Given запрос содержит поле email\\
When endpoint обрабатывает запрос\\
Then запись в логе содержит masked_email вместо оригинала и присутствует request_id


# Auth: все защищенные эндпоинты требуют валидной авторизации

Scenario: Запрос без заголовка авторизации отклоняется\\
Given сервис поднят на stage\\
When клиент делает GET /media/1 без заголовка X-User-Id\\
Then ответ 401 Unauthorized

# Owner: пользователь не может получить чужую запись

Scenario: Доступ к чужой media-записи запрещён\\
Given запись media с id=10 принадлежит user_id=42\\
And в базе есть user_id=100\\
When user_id=100 делает GET /media/10 с валидным заголовком\\
Then ответ 403 Forbidden

# Dependency management: CI падает при critical/high уязвимостях

Scenario: CI обнаружил критическую уязвимость в dependencies\\
Given requirements.txt содержит пакет с known critical CVE\\
When запускается job security_scan в CI\\
Then job завершился с non-zero exit и артефакт audit.json содержит уязвимость уровня CRITICAL or HIGH\\

# Input validation: некорректный payload возвращает 4xx

Scenario: Неправильный payload на создание записи\\
Given пользователь авторизован\\
When он делает POST /media/ с body {"title":"", "year": 99999}\\
Then ответ 422 Unprocessable Entity и тело ошибки содержит информацию по полям

# Rate limiting: защита от перебора

Scenario: Превышение лимита возвращает 429\\
Given для user_id=123 установлен лимит 120 req/min\\
When клиент делает >120 запросов за минуту к /media\\
Then некоторые ответы содержат 429 Too Many Requests\\

# Negative: логирование не должно содержать PII

Scenario: Логи не содержат незащищённую PII\\
Given запрос содержит поле email\\
When endpoint обрабатывает запрос\\
Then запись в логе содержит masked_email вместо оригинала и присутствует request_id
