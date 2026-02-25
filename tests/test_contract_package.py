import inspect

from pydantic import BaseModel

from packages.core import contracts
from packages.core.contracts.health import HealthResponse
from packages.core.contracts.jobs import JobEnvelope
from packages.core.contracts.meta import RuntimeMeta
from packages.core.contracts.tool_registry import (
    ToolRegistration,
    ToolRegistrySnapshot,
    ToolSpec,
)


def test_contract_package_exports_expected_symbols():
    expected = {
        "AgentSpec",
        "AgentRegistration",
        "AgentRegistrySnapshot",
        "ResponseError",
        "AgentResponseEnvelope",
        "ToolResponseEnvelope",
        "TraceContextContract",
        "ToolCallLogEntry",
        "SafetyDecision",
        "SafetyGateInput",
        "HealthResponse",
        "JobEnvelope",
        "LLMRequest",
        "LLMResponse",
        "LLMAdapterInfo",
        "RuntimeMeta",
        "ToolSpec",
        "ToolRegistration",
        "ToolRegistrySnapshot",
    }
    assert set(contracts.__all__) == expected


def test_exported_symbols_are_pydantic_models():
    for symbol_name in contracts.__all__:
        symbol = getattr(contracts, symbol_name)
        assert issubclass(symbol, BaseModel)


def test_contract_models_are_frozen_and_forbid_extra():
    models = [
        HealthResponse,
        RuntimeMeta,
        JobEnvelope,
        ToolSpec,
        ToolRegistration,
        ToolRegistrySnapshot,
    ]

    for model in models:
        assert model.model_config.get("frozen") is True
        assert model.model_config.get("extra") == "forbid"


def test_contract_package_has_no_fastapi_dependency():
    module_sources = [
        inspect.getsource(contracts),
        inspect.getsource(HealthResponse),
        inspect.getsource(RuntimeMeta),
        inspect.getsource(JobEnvelope),
        inspect.getsource(ToolSpec),
    ]
    merged_source = "\n".join(module_sources)

    assert "fastapi" not in merged_source.lower()
