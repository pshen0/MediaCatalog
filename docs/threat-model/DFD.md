# DFD — Data Flow Diagram (Media Catalog Service)

```mermaid
flowchart LR
    %% --- External Entity ---
    U[User / Client: Frontend or Postman]

    %% --- Trust Boundaries ---
    subgraph Edge[Trust Boundary: Edge Layer]
        API[FastAPI Router / API Gateway]
    end

    subgraph Core[Trust Boundary: Core Service]
        SVC[Media Service: CRUD, Validation]
    end

    subgraph Data[Trust Boundary: Data Storage]
        DB[(MEDIA_DB — In-Memory or Future DB)]
    end

    %% --- Data Flows ---
    U -->|F1: HTTPS + X-User-Id| API
    API -->|F2: Header Validation| SVC
    API -->|F3: POST / PUT JSON Payload| SVC
    API -->|F4: GET /list Query Params| SVC
    SVC -->|F5: CRUD Operations| DB
    DB -->|F6: Objects / Query Results| SVC
    SVC -->|F7: JSON Response| API
    API -->|F8: HTTPS Response| U
```

```mermaid
flowchart TB
    subgraph API_Layer[API Layer]
        A1[Auth Header Middleware]
        A2[Media Router]
    end

    subgraph Service_Layer[Service Layer]
        S1[Pydantic Validator]
        S2[Media CRUD Handler]
        S3[Logger / Audit Trail]
    end

    subgraph Data_Layer[Data Layer]
        D1[(InMemoryStorage)]
    end

    A1 --> A2 --> S1 --> S2 --> D1
    S2 --> S3
```

| ID | Описание потока                    | Тип данных                | Канал            | Примечание                    |
| -- | ---------------------------------- | ------------------------- | ---------------- | ----------------------------- |
| F1 | Клиент → API: запрос с `X-User-Id` | Метаданные аутентификации | HTTPS            | Симуляция авторизации         |
| F2 | API → Service: валидация заголовка | User ID                   | Внутренний вызов | Проверка авторства            |
| F3 | API → Service: POST/PUT JSON       | Media объект              | HTTP Body        | Потенциальный ввод            |
| F4 | API → Service: GET Query params    | Query                     | HTTP             | Фильтрация, сортировка        |
| F5 | Service → DB: CRUD операции        | dict                      | Внутренний канал | CRUD по owner_id              |
| F6 | DB → Service                       | dict                      | Внутренний канал | Данные по ID                  |
| F7 | Service → API                      | JSON                      | Внутренний вызов | Фильтрация результатов        |
| F8 | API → Клиент                       | JSON                      | HTTPS            | Возврат только своих объектов |
