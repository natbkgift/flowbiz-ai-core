"""Agent config loader.

Loads agent configuration from plain dicts (suitable for YAML/JSON
parsing upstream) and validates against the ``AgentConfig`` /
``AgentConfigSet`` contracts.  No file I/O is performed here — the
caller is responsible for reading the raw data.
"""

from __future__ import annotations

from typing import Any

from packages.core.contracts.agent_config import AgentConfig, AgentConfigSet


def load_agent_config(data: dict[str, Any]) -> AgentConfig:
    """Parse and validate a single agent configuration dict.

    Raises ``pydantic.ValidationError`` if the data is invalid.
    """
    return AgentConfig.model_validate(data)


def load_agent_config_set(data: dict[str, Any]) -> AgentConfigSet:
    """Parse and validate an ``AgentConfigSet`` from a dict.

    The dict is expected to have an ``agents`` key containing a list
    of agent configuration dicts.

    Raises ``pydantic.ValidationError`` if the data is invalid.
    """
    return AgentConfigSet.model_validate(data)


def load_agent_configs_from_list(items: list[dict[str, Any]]) -> AgentConfigSet:
    """Convenience: validate a list of dicts into an ``AgentConfigSet``."""
    return AgentConfigSet(agents=[AgentConfig.model_validate(d) for d in items])
