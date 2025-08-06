from typing import Any, List, Mapping, NamedTuple, Optional, Sequence

#from typing_extensions import Self

#from dagster import _check as check
from dagster._core.run_coordinator.base import SubmitRunContext
from dagster._core.run_coordinator.queued_run_coordinator import QueuedRunCoordinator
from dagster._core.storage.dagster_run import DagsterRun
#from dagster._serdes import ConfigurableClassData

# Constants
TAG_KEY = "code_location"

class CodeLocationTaggingQueuedRunCoordinator(QueuedRunCoordinator):
    """
    Automatically injects the fixed tag key 'code_location' before queueing.

    This lets you enforce tag-based concurrency limits per code server (code location)
    to cap the number of runs.
    """

    def submit_run(self, context: SubmitRunContext) -> DagsterRun:
        dagster_run: DagsterRun = context.dagster_run

        # Get the code location name from the run
        location_name = dagster_run.remote_job_origin.repository_origin.code_location_origin.location_name
        
        # Get required tags for this location
        required_tags = {TAG_KEY: location_name}
        
        # Find missing tags that need to be added
        to_add = {}
        for k, v in required_tags.items():
            if (dagster_run.tags or {}).get(k) != v:
                to_add[k] = v
        
        # Create a new DagsterRun with the additional tags if needed
        if to_add:
            # Merge existing tags with new tags
            updated_tags = {**(dagster_run.tags or {}), **to_add}
            dagster_run = dagster_run.with_tags(updated_tags)
        
        # Create a new context with the updated run
        updated_context = SubmitRunContext(
            dagster_run=dagster_run,
            workspace=context.workspace
        )
        
        return super().submit_run(updated_context)


# Short alias for config YAML convenience
class CLTQueuedRunCoordinator(CodeLocationTaggingQueuedRunCoordinator):
    """Short alias for config (same behavior)."""
    pass
