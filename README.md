# Dagster CLTQueuedRunCoordinator 

`CLTQueuedRunCoordinator` (Code Location Tagging Queued Run Coordinator) is a dagster custom run coordinator that adds a code location tag to all runs. All runs are tagged with the code location name with below format:

```
code_location:{code_location_name}
```

`CLTQueuedRunCoordinator` helps you enforce tag-based concurrency limits for each code server (code location), allowing you to cap the number of Dagster runs on Kubernetes. It inherits from `QueuedRunCoordinator`, so it supports all of the same configuration options.

## How to use

To use the `CLTQueuedRunCoordinator`, you must configure the Dagster daemon, the Dagster web server, and the Dagster code-location server.

### Dagster Daemon

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
              value: "code_location_a"
              limit: 10
            - key: "code_location"
              value: "code_location_b"
              limit: 20
```

* Container Image : `ghcr.io/ssup2/dagster-clt-queued-run-coordinator:<release-version>`

### Web Server

```yaml
dagsterWebServer:
  enabled: true

  image:
    repository: "ghcr.io/ssup2/dagster-clt-queued-run-coordinator"
    tag: "1.10.5"
    pullPolicy: Always
```

* Container Image : `ghcr.io/ssup2/dagster-clt-queued-run-coordinator:<release-version>`

### Code Server

