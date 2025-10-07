| NFR ID | Story/Task.                                                  | Приоритет | Release/Milestone |
| ------ | ------------------------------------------------------------ | --------- | ----------------- |
| NFR-01 | AUTH-01: Add `get_current_user` dependency + auth middleware | High      | next-release      |
| NFR-02 | MEDIA-02: Enforce owner checks on media CRUD                 | High      | next-release      |
| NFR-03 | API-VALID-01: Validate all payloads with Pydantic schemas    | High      | next-release      |
| NFR-04 | CI-DEP-01: Add `pip-audit` and schedule weekly SCA scans     | High      | next-release      |
| NFR-05 | CI-SAST-01: Add `semgrep` and `bandit` jobs to CI            | High      | next-release      |
| NFR-06 | REPO-SEC-01: Add `detect-secrets` pre-commit hook            | High      | next-release      |
| NFR-07 | AUTH-02: Configure JWT TTL & refresh policy (≤1h / ≤30d)     | Medium    | next-release      |
| NFR-08 | LOG-01: Add `correlation_id` and PII masking in logs         | Medium    | next-release      |
| NFR-09 | STORAGE-01: Encrypt sensitive user/media fields              | Medium    | next-release      |
| NFR-10 | PERF-01: Load test `/media` p95 latency (≤300ms)             | Medium    | p03-nfr           |
| NFR-11 | EDGE-01: Add rate limiting (120 req/min per user/IP)         | Medium    | next-release      |
