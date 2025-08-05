from dagster._core.run_coordinator.queued_run_coordinator import QueuedRunCoordinator

from .utils import (
    get_code_location_name,
    required_tags_for_location,
    missing_tags,
)

class CodeLocationTaggingQueuedRunCoordinator(QueuedRunCoordinator):
    """
    Automatically injects the fixed tag key 'code_location' before queueing.

    This lets you enforce tag-based concurrency limits per code server (code location)
    to cap the number of runs.
    """

    def submit_run(self, context, dagster_run):
        to_add = missing_tags(
            getattr(dagster_run, "tags", {}) or {},
            required_tags_for_location(get_code_location_name(dagster_run)),
        )
        if to_add:
            context.instance.add_run_tags(dagster_run.run_id, to_add)
            context.log.info(f"CLT Queued Run Coordinator injected tags for run_id={dagster_run.run_id}: {to_add}")
        return super().submit_run(context, dagster_run)


# Short alias for config YAML convenience
class CLTQueuedRunCoordinator(CodeLocationTaggingQueuedRunCoordinator):
    """Short alias for config (same behavior)."""
    pass
