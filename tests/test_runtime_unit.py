"""Unit tests for PR-022 runtime components."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from packages.core.runtime import (
    AgentRuntime,
    RuntimeContext,
    RuntimeRequest,
    RuntimeResult,
)
from packages.core.runtime.agents import EchoAgent
from packages.core.runtime.request import RuntimeRequestMeta
from packages.core.runtime.result import RuntimeError
from packages.core.safety_gate import SafetyGateProtocol


class TestRuntimeRequestMeta:
    """Unit tests for RuntimeRequestMeta schema."""

    def test_meta_defaults(self):
        """Verify RuntimeRequestMeta has correct defaults."""
        meta = RuntimeRequestMeta()

        assert meta.trace_id is None
        assert meta.mode == "dev"

    def test_meta_with_values(self):
        """Verify RuntimeRequestMeta accepts custom values."""
        meta = RuntimeRequestMeta(trace_id="custom-123", mode="prod")

        assert meta.trace_id == "custom-123"
        assert meta.mode == "prod"

    def test_meta_extra_fields_rejected(self):
        """Verify extra fields are rejected (strict schema)."""
        with pytest.raises(ValidationError) as exc_info:
            RuntimeRequestMeta(trace_id="test", unknown_field="fail")

        assert "unknown_field" in str(exc_info.value)


class TestRuntimeRequest:
    """Unit tests for RuntimeRequest schema."""

    def test_request_minimal(self):
        """Verify RuntimeRequest works with minimal required fields."""
        req = RuntimeRequest(agent="echo", input="test")

        assert req.agent == "echo"
        assert req.input == "test"
        assert isinstance(req.meta, RuntimeRequestMeta)
        assert req.meta.trace_id is None
        assert req.meta.mode == "dev"

    def test_request_with_meta(self):
        """Verify RuntimeRequest accepts custom meta."""
        req = RuntimeRequest(
            agent="echo",
            input="test",
            meta=RuntimeRequestMeta(trace_id="custom-123", mode="prod"),
        )

        assert req.agent == "echo"
        assert req.input == "test"
        assert req.meta.trace_id == "custom-123"
        assert req.meta.mode == "prod"

    def test_request_meta_default_factory(self):
        """Verify meta uses default_factory correctly."""
        req1 = RuntimeRequest(agent="echo", input="test1")
        req2 = RuntimeRequest(agent="echo", input="test2")

        # Each should get its own meta instance
        assert req1.meta is not req2.meta

    def test_request_missing_agent(self):
        """Verify missing 'agent' field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RuntimeRequest(input="test")

        assert "agent" in str(exc_info.value)

    def test_request_missing_input(self):
        """Verify missing 'input' field raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            RuntimeRequest(agent="echo")

        assert "input" in str(exc_info.value)

    def test_request_extra_fields_rejected(self):
        """Verify extra fields are rejected (strict schema)."""
        with pytest.raises(ValidationError) as exc_info:
            RuntimeRequest(agent="echo", input="test", unknown_field="fail")

        assert "unknown_field" in str(exc_info.value)


class TestRuntimeError:
    """Unit tests for RuntimeError schema."""

    def test_error_creation(self):
        """Verify RuntimeError can be created with all fields."""
        err = RuntimeError(
            code="AGENT_NOT_FOUND",
            message="Agent not found",
            details={"agent": "unknown"},
        )

        assert err.code == "AGENT_NOT_FOUND"
        assert err.message == "Agent not found"
        assert err.details == {"agent": "unknown"}

    def test_error_frozen(self):
        """Verify RuntimeError is frozen (immutable)."""
        err = RuntimeError(code="RUNTIME_ERROR", message="Test", details={})

        with pytest.raises(ValidationError):
            err.code = "VALIDATION_ERROR"

    def test_error_code_validation(self):
        """Verify error code is validated against allowed values."""
        # Valid codes
        RuntimeError(code="VALIDATION_ERROR", message="test")
        RuntimeError(code="AGENT_NOT_FOUND", message="test")
        RuntimeError(code="RUNTIME_ERROR", message="test")

        # Invalid code
        with pytest.raises(ValidationError):
            RuntimeError(code="INVALID_CODE", message="test")


class TestRuntimeResult:
    """Unit tests for RuntimeResult schema."""

    def test_result_success(self):
        """Verify RuntimeResult for successful execution."""
        result = RuntimeResult(
            status="ok",
            trace_id="test-123",
            agent="echo",
            output="hello",
        )

        assert result.status == "ok"
        assert result.trace_id == "test-123"
        assert result.agent == "echo"
        assert result.output == "hello"
        assert result.errors == []

    def test_result_error(self):
        """Verify RuntimeResult for error case."""
        err = RuntimeError(code="AGENT_NOT_FOUND", message="Not found", details={})
        result = RuntimeResult(
            status="error",
            trace_id="test-123",
            agent="unknown",
            output=None,
            errors=[err],
        )

        assert result.status == "error"
        assert result.trace_id == "test-123"
        assert result.agent == "unknown"
        assert result.output is None
        assert len(result.errors) == 1
        assert result.errors[0].code == "AGENT_NOT_FOUND"

    def test_result_errors_default_factory(self):
        """Verify errors list uses default_factory correctly."""
        result1 = RuntimeResult(status="ok", trace_id="1", agent="a", output="x")
        result2 = RuntimeResult(status="ok", trace_id="2", agent="b", output="y")

        # Each should get its own errors list
        assert result1.errors is not result2.errors

    def test_result_status_validation(self):
        """Verify status is validated against allowed values."""
        # Valid statuses
        RuntimeResult(status="ok", trace_id="1", agent="a", output="x")
        RuntimeResult(status="error", trace_id="2", agent="b", output=None)

        # Invalid status
        with pytest.raises(ValidationError):
            RuntimeResult(status="invalid", trace_id="1", agent="a", output="x")

    def test_result_extra_fields_rejected(self):
        """Verify extra fields are rejected (strict schema)."""
        with pytest.raises(ValidationError) as exc_info:
            RuntimeResult(
                status="ok",
                trace_id="1",
                agent="a",
                output="x",
                unknown_field="fail",
            )

        assert "unknown_field" in str(exc_info.value)


class TestRuntimeContext:
    """Unit tests for RuntimeContext."""

    def test_context_creation(self):
        """Verify RuntimeContext is created with all fields."""
        ctx = RuntimeContext(
            agent="echo",
            input="hello",
            trace_id="custom-123",
            mode="prod",
            meta={"key": "value"},
        )

        assert ctx.agent == "echo"
        assert ctx.input == "hello"
        assert ctx.trace_id == "custom-123"
        assert ctx.mode == "prod"
        assert ctx.meta == {"key": "value"}

    def test_context_trace_id_generation(self):
        """Verify trace_id is generated if not provided."""
        ctx = RuntimeContext(agent="echo", input="test")

        assert ctx.trace_id is not None
        assert len(ctx.trace_id) > 0
        # Should be valid UUID format
        try:
            uuid.UUID(ctx.trace_id)
        except ValueError:
            pytest.fail("trace_id is not a valid UUID")

    def test_context_defaults(self):
        """Verify RuntimeContext has correct defaults."""
        ctx = RuntimeContext(agent="echo", input="test")

        assert ctx.mode == "dev"
        assert ctx.meta == {}

    def test_context_meta_not_shared(self):
        """Verify meta dict is not shared between instances."""
        ctx1 = RuntimeContext(agent="echo", input="test1")
        ctx2 = RuntimeContext(agent="echo", input="test2")

        # Each should get its own meta dict
        assert ctx1.meta is not ctx2.meta


class TestEchoAgent:
    """Unit tests for EchoAgent."""

    def test_echo_agent_name(self):
        """Verify EchoAgent has correct name."""
        agent = EchoAgent()

        assert agent.name == "echo"

    def test_echo_agent_execute(self):
        """Verify EchoAgent echoes input to output."""
        agent = EchoAgent()
        ctx = RuntimeContext(agent="echo", input="hello world", trace_id="test-123")

        result = agent.execute(ctx)

        assert result.status == "ok"
        assert result.output == "hello world"
        assert result.agent == "echo"
        assert result.trace_id == "test-123"
        assert result.errors == []

    def test_echo_agent_preserves_trace_id(self):
        """Verify EchoAgent preserves trace_id from context."""
        agent = EchoAgent()
        custom_trace_id = "custom-trace-456"
        ctx = RuntimeContext(agent="echo", input="test", trace_id=custom_trace_id)

        result = agent.execute(ctx)

        assert result.trace_id == custom_trace_id

    def test_echo_agent_deterministic(self):
        """Verify EchoAgent produces deterministic output."""
        agent = EchoAgent()
        test_input = "deterministic test"
        ctx = RuntimeContext(agent="echo", input=test_input)

        result1 = agent.execute(ctx)
        result2 = agent.execute(ctx)

        assert result1.output == result2.output
        assert result1.output == test_input


class TestAgentRuntime:
    """Unit tests for AgentRuntime."""

    def test_runtime_initialization(self):
        """Verify AgentRuntime initializes with built-in agents."""
        runtime = AgentRuntime()

        # Should have echo agent registered
        assert "echo" in runtime._agents
        assert isinstance(runtime._agents["echo"], EchoAgent)

    def test_runtime_execute_echo(self):
        """Verify AgentRuntime can execute echo agent."""
        runtime = AgentRuntime()
        ctx = RuntimeContext(agent="echo", input="test message")

        result = runtime.run(ctx)

        assert result.status == "ok"
        assert result.output == "test message"
        assert result.agent == "echo"

    def test_runtime_unknown_agent(self):
        """Verify AgentRuntime returns AGENT_NOT_FOUND for unknown agent."""
        runtime = AgentRuntime()
        ctx = RuntimeContext(agent="unknown", input="test")

        result = runtime.run(ctx)

        assert result.status == "error"
        assert result.agent == "unknown"
        assert result.output is None
        assert len(result.errors) == 1
        assert result.errors[0].code == "AGENT_NOT_FOUND"
        assert "unknown" in result.errors[0].message

    def test_runtime_preserves_trace_id(self):
        """Verify AgentRuntime preserves trace_id from context."""
        runtime = AgentRuntime()
        custom_trace_id = "custom-789"
        ctx = RuntimeContext(agent="echo", input="test", trace_id=custom_trace_id)

        result = runtime.run(ctx)

        assert result.trace_id == custom_trace_id

    def test_runtime_disable_agent_blocks_execution(self):
        """Verify disabling an agent prevents execution."""
        runtime = AgentRuntime()
        runtime.disable_agent("echo")

        result = runtime.run(RuntimeContext(agent="echo", input="blocked"))

        assert result.status == "error"
        assert result.agent == "echo"
        assert result.output is None
        assert len(result.errors) == 1
        assert result.errors[0].code == "AGENT_NOT_FOUND"

    def test_runtime_reenable_agent_allows_execution(self):
        """Verify re-enabling an agent restores execution."""
        runtime = AgentRuntime()
        runtime.disable_agent("echo")
        runtime.enable_agent("echo")

        result = runtime.run(RuntimeContext(agent="echo", input="allowed"))

        assert result.status == "ok"
        assert result.output == "allowed"

    def test_runtime_exception_handling(self):
        """Verify AgentRuntime handles agent exceptions gracefully."""
        runtime = AgentRuntime()

        # Create a mock failing agent
        class FailingAgent:
            name = "failing"

            def execute(self, ctx):
                raise ValueError("Intentional failure")

        runtime._agents["failing"] = FailingAgent()
        ctx = RuntimeContext(agent="failing", input="test")

        result = runtime.run(ctx)

        assert result.status == "error"
        assert result.agent == "failing"
        assert result.output is None
        assert len(result.errors) == 1
        assert result.errors[0].code == "RUNTIME_ERROR"
        assert "Intentional failure" in result.errors[0].message

    def test_runtime_safety_gate_denies_execution(self):
        """Verify optional safety gate can block execution before agent runs."""

        class DenyGate(SafetyGateProtocol):
            def check(self, payload):
                from packages.core.contracts.safety import SafetyDecision

                return SafetyDecision(
                    decision="deny",
                    reason="Blocked by policy",
                    code="POLICY_BLOCK",
                )

        runtime = AgentRuntime(safety_gate=DenyGate())
        result = runtime.run(RuntimeContext(agent="echo", input="blocked"))

        assert result.status == "error"
        assert len(result.errors) == 1
        assert result.errors[0].code == "VALIDATION_ERROR"
        assert "Blocked by policy" in result.errors[0].message
