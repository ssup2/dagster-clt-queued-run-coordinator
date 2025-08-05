# CLTQueuedRunCoordinator (simplified)

**CLTQueuedRunCoordinator** (aka `CodeLocationTaggingQueuedRunCoordinator`)는 Dagster OSS에서
런이 큐잉되기 전에 **코드 로케이션(Code Location) 기반 태그를 자동 주입**하여
`tag_concurrency_limits`를 안정적으로 적용하게 해 주는 커스텀 Run Coordinator입니다.

이번 버전은 **설정을 모두 제거**하고, 태그 키를 **고정: `code_location`** 으로 사용합니다.
- 어떤 로케이션에서 생성된 Run이든 자동으로 `{"code_location": "<location_name>"}` 태그가 붙습니다.
- 웹서버/데몬은 **하나의 인스턴스**로 유지
- 개발자가 태그를 빼먹어도 **컨트롤 플레인에서 보정**

> 구현 클래스: `CodeLocationTaggingQueuedRunCoordinator`  
> 설정용 별칭: `CLTQueuedRunCoordinator`

---

## 설치

```bash
git clone <this-repo-url>
cd clt-queued-run-coordinator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 사용법

1) **패키지 배포/배치**  
웹서버/데몬이 사용하는 이미지(또는 venv)에 본 패키지를 포함시킵니다.

2) **`dagster.yaml` 설정**

```yaml
run_coordinator:
  module: clt_queued_run_coordinator.coordinator
  class: CLTQueuedRunCoordinator   # 별칭 사용
  config:
    max_concurrent_runs: 40
    tag_concurrency_limits:
      - key: "code_location"
        value: "A"
        limit: 10
      - key: "code_location"
        value: "B"
        limit: 20
```

> 이제 추가적인 환경변수/설정은 필요하지 않습니다.

---

## 동작 개요

- 모든 Run 제출 경로(UI/스케줄/센서/CLI/백필)는 **Run Coordinator를 경유**합니다.
- 본 Coordinator는 귀속 **Code Location 이름을 추출**하고, 필요하면 `{"code_location": "<loc>"}` 태그를 **강제 주입**합니다.
- 이후 기본 `QueuedRunCoordinator` 로직(큐/동시성 체크)을 그대로 이어갑니다.

---

## 개발

- 코드: `src/clt_queued_run_coordinator/`
- 테스트: `pytest`
- 린트/포맷: `ruff`, `black`

```bash
pytest -q
ruff check . && black --check .
```

---

## 라이선스

MIT
