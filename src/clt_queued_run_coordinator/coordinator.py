from __future__ import annotations

from typing import Mapping

# Dagster 1.10.5 import (no compatibility branches)
from dagster._core.run_coordinator.queued_run_coordinator import QueuedRunCoordinator

from .utils import (
    get_code_location_name,
    required_tags_for_location,
    missing_tags,
)


class CodeLocationTaggingQueuedRunCoordinator(QueuedRunCoordinator):
    """
    A QueuedRunCoordinator that auto-injects a fixed tag key 'code_location' BEFORE queueing,
    so tag-based concurrency limits will apply even if user code forgot to set tags.
    """

    def submit_run(self, context, dagster_run):
        # 1) Determine code location name
        loc = get_code_location_name(dagster_run)

        # 2) Required tags (fixed key: 'code_location')
        required = required_tags_for_location(loc)

        # 3) Inject missing tags at the instance level
        existing: Mapping[str, str] = getattr(dagster_run, "tags", {}) or {}
        to_add = missing_tags(existing, required)
        if to_add:
            try:
                context.instance.add_run_tags(dagster_run.run_id, to_add)
                context.log.info(
                    f"CLTQRC injected tags for run_id={dagster_run.run_id}: {to_add} (loc={loc})"
                )
            except Exception as e:
                # Keep best-effort behavior (not related to old-version compatibility)
                context.log.warning(f"CLTQRC warning: failed to add tags: {e}")

        # 4) Delegate to base (queueing & concurrency checks)
        return super().submit_run(context, dagster_run)


# Short alias for config YAML convenience
class CLTQueuedRunCoordinator(CodeLocationTaggingQueuedRunCoordinator):
    """Short alias for config (same behavior)."""
    pass
