# Dagster CLTQueuedRunCoordinator 

Dagster `CLTQueuedRunCoordinator` (Code Location Tagging Queued Run Coordinator) is a custom run coordinator that adds a code location tag to all runs. This is useful for enforcing tag-based concurrency limits per code server (code location) to cap the number of runs.

`CLTQueuedRunCoordinator` inherits from `QueuedRunCoordinator` and supports all the same configuration options. All runs are tagged with the code location name with below format:

```
code_location:{code_location_name}
```

## How to use

### Daemon

```yaml
dagsterDaemon:
  enabled: true

  image:
    repository: "ghcr.io/ssup2/dagster-clt-queued-run-coordinator"
    tag: "1.10.5"
    pullPolicy: Always

  runCoordinator:
    enabled: true

    type: CustomRunCoordinator
    config:
      customRunCoordinator:
        module: clt_queued_run_coordinator.coordinator
        class: CLTQueuedRunCoordinator
        config:
          dequeue_interval_seconds: 5
          dequeue_use_threads: true
          dequeue_num_workers: 4
          tag_concurrency_limits:
            - key: "code_location"
              value: "dagster-workflows"
              limit: 2
```

### Web Server

```yaml
dagsterWebServer:
  enabled: true

  image:
    repository: "ghcr.io/ssup2/dagster-clt-queued-run-coordinator"
    tag: "1.10.5"
    pullPolicy: Always
```

### Code Server

