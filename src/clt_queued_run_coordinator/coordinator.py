from dagster._core.instance import DagsterInstance
from dagster._core.run_coordinator.base import SubmitRunContext
from dagster._core.run_coordinator.queued_run_coordinator import QueuedRunCoordinator
from dagster._core.storage.dagster_run import DagsterRun

CLT_TAG_KEY = "code_location"

class CodeLocationTaggingQueuedRunCoordinator(QueuedRunCoordinator):
    """
    Automatically injects the fixed tag key 'code_location' before queueing.

    This lets you enforce tag-based concurrency limits per code server (code location)
    to cap the number of runs.
    """

    def submit_run(self, context: SubmitRunContext) -> DagsterRun:
        # Init variables
        dagster_run: DagsterRun = context.dagster_run
        location_name = dagster_run.remote_job_origin.repository_origin.code_location_origin.location_name
        
        # Check if code_location tag needs to be added
        current_tags = dagster_run.tags or {}
        if current_tags.get(CLT_TAG_KEY) != location_name:
            # Add the code_location tag
            DagsterInstance.get().add_run_tags(dagster_run.run_id, {CLT_TAG_KEY: location_name})
        
        # Submit the updated run
        return super().submit_run(context)

# Short alias for config YAML convenience
class CLTQueuedRunCoordinator(CodeLocationTaggingQueuedRunCoordinator):
    """Short alias for config (same behavior)."""
    pass
