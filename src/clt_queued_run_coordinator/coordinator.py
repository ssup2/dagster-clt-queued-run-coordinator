from typing import Any, List, Mapping, NamedTuple, Optional, Sequence

from typing_extensions import Self

from dagster import _check as check
from dagster._core.run_coordinator.base import SubmitRunContext
from dagster._core.run_coordinator.queued_run_coordinator import QueuedRunCoordinator
from dagster._core.storage.dagster_run import DagsterRun
from dagster._serdes import ConfigurableClassData

# Constants
TAG_KEY = "code_location"

class RunQueueConfig(
    NamedTuple(
        "_RunQueueConfig",
        [
            ("max_concurrent_runs", int),
            ("tag_concurrency_limits", Sequence[Mapping[str, Any]]),
            ("max_user_code_failure_retries", int),
            ("user_code_failure_retry_delay", int),
            ("should_block_op_concurrency_limited_runs", bool),
            ("op_concurrency_slot_buffer", int),
        ],
    )
):
    def __new__(
        cls,
        max_concurrent_runs: int,
        tag_concurrency_limits: Optional[Sequence[Mapping[str, Any]]],
        max_user_code_failure_retries: int = 0,
        user_code_failure_retry_delay: int = 60,
        should_block_op_concurrency_limited_runs: bool = True,
        op_concurrency_slot_buffer: int = 0,
    ):
        return super().__new__(
            cls,
            check.int_param(max_concurrent_runs, "max_concurrent_runs"),
            check.opt_sequence_param(tag_concurrency_limits, "tag_concurrency_limits"),
            check.int_param(max_user_code_failure_retries, "max_user_code_failure_retries"),
            check.int_param(user_code_failure_retry_delay, "user_code_failure_retry_delay"),
            check.bool_param(should_block_op_concurrency_limited_runs, "should_block_op_concurrency_limited_runs"),
            check.int_param(op_concurrency_slot_buffer, "op_concurrency_slot_buffer"),
        )

    def with_concurrency_settings(
        self, concurrency_settings: Mapping[str, Any]
    ) -> "RunQueueConfig":
        run_settings = concurrency_settings.get("runs", {})
        pool_settings = concurrency_settings.get("pools", {})
        return RunQueueConfig(
            max_concurrent_runs=run_settings.get("max_concurrent_runs", self.max_concurrent_runs),
            tag_concurrency_limits=run_settings.get("tag_concurrency_limits", self.tag_concurrency_limits),
            max_user_code_failure_retries=self.max_user_code_failure_retries,
            user_code_failure_retry_delay=self.user_code_failure_retry_delay,
            should_block_op_concurrency_limited_runs=self.should_block_op_concurrency_limited_runs,
            op_concurrency_slot_buffer=pool_settings.get("op_granularity_run_buffer", self.op_concurrency_slot_buffer),
        )

class CodeLocationTaggingQueuedRunCoordinator(QueuedRunCoordinator):
    """
    Automatically injects the fixed tag key 'code_location' before queueing.

    This lets you enforce tag-based concurrency limits per code server (code location)
    to cap the number of runs.
    """

    def __init__(
        self,
        max_concurrent_runs: Optional[int] = None,
        tag_concurrency_limits: Optional[List[Mapping[str, Any]]] = None,
        dequeue_interval_seconds: Optional[int] = None,
        dequeue_use_threads: Optional[bool] = None,
        dequeue_num_workers: Optional[int] = None,
        max_user_code_failure_retries: Optional[int] = None,
        user_code_failure_retry_delay: Optional[int] = None,
        block_op_concurrency_limited_runs: Optional[Mapping[str, Any]] = None,
        inst_data: Optional[ConfigurableClassData] = None,
    ):
        super().__init__(
            max_concurrent_runs=max_concurrent_runs,
            tag_concurrency_limits=tag_concurrency_limits,
            dequeue_interval_seconds=dequeue_interval_seconds,
            dequeue_use_threads=dequeue_use_threads,
            dequeue_num_workers=dequeue_num_workers,
            max_user_code_failure_retries=max_user_code_failure_retries,
            user_code_failure_retry_delay=user_code_failure_retry_delay,
            block_op_concurrency_limited_runs=block_op_concurrency_limited_runs,
            inst_data=inst_data,
        )

    def get_run_queue_config(self) -> RunQueueConfig:
        return RunQueueConfig(
            max_concurrent_runs=self._max_concurrent_runs,
            tag_concurrency_limits=self._tag_concurrency_limits,
            max_user_code_failure_retries=self._max_user_code_failure_retries,
            user_code_failure_retry_delay=self._user_code_failure_retry_delay,
            should_block_op_concurrency_limited_runs=self._should_block_op_concurrency_limited_runs,
            op_concurrency_slot_buffer=self._op_concurrency_slot_buffer,
        )

    @classmethod
    def config_type(cls):
        parent_config = super().config_type()
        return {**parent_config}

    @classmethod
    def from_config_value(
        cls, inst_data: ConfigurableClassData, config_value: Mapping[str, Any]
    ) -> Self:
        return cls(
            inst_data=inst_data,
            max_concurrent_runs=config_value.get("max_concurrent_runs"),
            tag_concurrency_limits=config_value.get("tag_concurrency_limits"),
            dequeue_interval_seconds=config_value.get("dequeue_interval_seconds"),
            dequeue_use_threads=config_value.get("dequeue_use_threads"),
            dequeue_num_workers=config_value.get("dequeue_num_workers"),
            max_user_code_failure_retries=config_value.get("max_user_code_failure_retries"),
            user_code_failure_retry_delay=config_value.get("user_code_failure_retry_delay"),
            block_op_concurrency_limited_runs=config_value.get("block_op_concurrency_limited_runs"),
        )

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
