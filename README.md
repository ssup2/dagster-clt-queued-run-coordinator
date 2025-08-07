# Dagster CLTQueuedRunCoordinator 

`CLTQueuedRunCoordinator` (Code-Location Tagging Queued Run Coordinator) is a custom Dagster run coordinator that automatically tags every run with its code-location name. Each run receives a tag in the following format:

```
code_location:{code_location_name}
```

`CLTQueuedRunCoordinator` helps you enforce tag-based concurrency limits for each code server (code location), allowing you to cap the number of Dagster runs on Kubernetes. It inherits from `QueuedRunCoordinator`, so it supports all of the same configuration options.

## How to use

To use the `CLTQueuedRunCoordinator`, you must configure the Dagster daemon, the Dagster web server, and the Dagster code-location server.

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
              value: "code-location-a"
              limit: 10
            - key: "code_location"
              value: "code-location-b"
              limit: 20
```

Set the run coordinator to CustomRunCoordinator, and configure CLTQueuedRunCoordinator with the values below:

* Container Image : `ghcr.io/ssup2/dagster-clt-queued-run-coordinator:<release-version>`
* Coordinator Module :  `clt_queued_run_coordinator.coordinator`
* Coordinator Class : `CLTQueuedRunCoordinator`
* Config : Uses the same settings as `QueuedRunCoordinator`, but all option names are in **snake_case** rather than **PascalCase** (e.g., `DequeueIntervalSeconds` → `dequeue_interval_seconds`).
  * With the `tag_concurrency_limits` option, you can define per-code-location concurrency limits by using the `code_location` tag.

### Web Server

```yaml
dagsterWebServer:
  enabled: true

  image:
    repository: "ghcr.io/ssup2/dagster-clt-queued-run-coordinator"
    tag: "1.10.5"
    pullPolicy: Always
```

Set the web server image to the same image as the daemon.

* Container Image : `ghcr.io/ssup2/dagster-clt-queued-run-coordinator:<release-version>`

### Code Location Server

```shell
# pip
pip install dagster-clt-queued-run-coordinator

# uv
uv add dagster-clt-queued-run-coordinator
```

Code Location Server must install the `dagster-clt-queued-run-coordinator` python package.


