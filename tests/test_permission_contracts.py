import json

import pytest
from pydantic import ValidationError

from packages.core.tools import (
    AgentPolicy,
    Permission,
    PolicyDecision,
    ToolBase,
    ToolContext,
    ToolPermissions,
    ToolResult,
    authorize,
)


class _SampleTool(ToolBase):
    @property
    def name(self) -> str:  # pragma: no cover - trivial property
        return "sample_tool"

    @property
    def description(self) -> str:  # pragma: no cover - trivial property
        return "Sample tool for contract tests"

    def run(self, context: ToolContext) -> ToolResult:  # pragma: no cover - stub
        return ToolResult(
            ok=True,
            data={},
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )


def test_models_are_immutable():
    tool_permissions = ToolPermissions(required_permissions=(Permission.READ_FS,))
    policy = AgentPolicy(
        persona="core",
        allowed_permissions=(Permission.READ_FS,),
        allowed_tools=("sample_tool",),
    )
    decision = PolicyDecision(allowed=True, reason="design-only")

    with pytest.raises((TypeError, ValidationError)):
        tool_permissions.required_permissions = ()

    with pytest.raises((TypeError, ValidationError)):
        policy.persona = "docs"

    with pytest.raises((TypeError, ValidationError)):
        decision.allowed = False


def test_json_round_trip():
    original_permissions = ToolPermissions(
        required_permissions=[Permission.EXEC_SHELL, Permission.READ_ENV],
        optional_permissions=[Permission.NET_HTTP],
    )
    original_policy = AgentPolicy(
        persona="infra",
        allowed_permissions=[
            Permission.EXEC_SHELL,
            Permission.READ_ENV,
            Permission.NET_HTTP,
        ],
        allowed_tools=[],
    )
    original_decision = PolicyDecision(allowed=True, reason="all good")

    permissions_json = original_permissions.model_dump_json()
    policy_json = original_policy.model_dump_json()
    decision_json = original_decision.model_dump_json()

    loaded_permissions = ToolPermissions.model_validate_json(permissions_json)
    loaded_policy = AgentPolicy.model_validate_json(policy_json)
    loaded_decision = PolicyDecision.model_validate_json(decision_json)

    assert loaded_permissions == original_permissions
    assert loaded_policy == original_policy
    assert loaded_decision == original_decision

    # Ensure JSON is deterministic and serializable through the standard json module
    assert json.loads(decision_json)["allowed"] is True


def test_authorize_returns_allow_decision():
    tool = _SampleTool()
    context = ToolContext(trace_id="trace-123", agent_id="agent-1")
    policy = AgentPolicy(
        persona="core",
        allowed_permissions=[Permission.READ_FS],
        allowed_tools=[tool.name],
    )

    decision = authorize(tool=tool, ctx=context, policy=policy)

    assert isinstance(decision, PolicyDecision)
    assert decision.allowed is True
    assert "design-only" in decision.reason
