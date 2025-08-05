from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

TAG_KEY = "code_location"


def get_code_location_name(dagster_run: Any) -> Optional[str]:
    """
    Retrieve the code location name from a Dagster run (Dagster 1.10.5).
    """
    origin = getattr(dagster_run, "external_job_origin", None)
    return getattr(origin, "location_name", None) if origin else None


def required_tags_for_location(location_name: Optional[str]) -> Mapping[str, str]:
    """
    Return required tags for a given code location.
    If no location is available, return {} (no tagging).
    """
    if not location_name:
        return {}
    return {TAG_KEY: location_name}


def missing_tags(existing: Mapping[str, str], required: Mapping[str, str]) -> Dict[str, str]:
    """
    Compute which (key, value) pairs from required are missing or different in existing.
    """
    to_add: Dict[str, str] = {}
    for k, v in required.items():
        if existing.get(k) != v:
            to_add[k] = v
    return to_add
