# Tool Authoring Guide

This document is the **single source of truth** for writing Tools in FlowBiz AI Core.

Tools are deterministic, testable units of capability that execute specific actions without decision-making logic. This guide defines what a Tool is, how to write one correctly, and how to ensure it integrates seamlessly with the Agent Runtime and Tool Registry.

**Audience:** Core developers, Infrastructure developers, Documentation authors, Agent authors

---

## Table of Contents

1. [What is a Tool?](#what-is-a-tool)
2. [Tool Contract (Interface)](#tool-contract-interface)
3. [Tool Lifecycle (Mental Model)](#tool-lifecycle-mental-model)
4. [Authoring Rules (Hard Rules)](#authoring-rules-hard-rules)
5. [Error Design Guidelines](#error-design-guidelines)
6. [Example: DummyTool (Reference)](#example-dummytool-reference)
7. [Testing a Tool](#testing-a-tool)
8. [Tool Readiness Checklist](#tool-readiness-checklist)
9. [Future Extensions (Non-binding)](#future-extensions-non-binding)
10. [Out of Scope](#out-of-scope)

---

## What is a Tool?

A Tool is a **unit of deterministic capability**.

### Core Principles

**Tools do not "think" — Tools only "do"**

A Tool performs a specific, predictable action based on its inputs. It has no decision-making logic, no agent-level business rules, and no awareness of the broader system context beyond what's explicitly passed to it.

### What a Tool IS

- ✅ A deterministic function: same input → same output
- ✅ A pure transformation: input data → output data
- ✅ An isolated capability: performs one specific action
- ✅ Testable without external dependencies
- ✅ Immediately usable by Agent Runtime or Tool Registry

### What a Tool IS NOT

- ❌ An agent (no decision-making)
- ❌ A business logic controller (no orchestration)
- ❌ A stateful component (no memory between calls)
- ❌ A direct API client (infrastructure should be injected)
- ❌ A logging service (runtime handles logging)

### Mental Model

Think of a Tool as a function in the mathematical sense:

```
f(x) = y
```

Given input `x`, it always produces output `y`. No side effects, no surprises.

**Example:**
- ✅ GOOD: A tool that validates email format
- ✅ GOOD: A tool that performs arithmetic operations
- ✅ GOOD: A tool that transforms text to uppercase
- ❌ BAD: A tool that "decides" which other tool to call
- ❌ BAD: A tool that generates random outputs
- ❌ BAD: A tool that reads configuration from environment variables

---

## Tool Contract (Interface)

Every Tool must conform to the following contract to be compatible with the Tool Registry and Agent Runtime.

### Base Interface

```python
class ToolBase:
    """Abstract base class for all Tools."""
    
    name: str           # Unique identifier for the tool
    description: str    # Human-readable description of what the tool does
    version: str        # Semantic version (e.g., "1.0.0")
    
    def run(self, context: ToolContext) -> ToolResult:
        """
        Execute the tool's primary function.
        
        Args:
            context: ToolContext containing input parameters and metadata
            
        Returns:
            ToolResult with success/failure status and output data
        """
        ...
```

### ToolContext

`ToolContext` provides the input and metadata needed for tool execution:

```python
class ToolContext:
    """Context passed to a tool during execution."""
    
    trace_id: str                    # End-to-end execution tracing identifier
    parameters: dict[str, Any]       # Tool-specific input parameters
    metadata: dict[str, Any] | None  # Optional execution metadata
```

**Key Concepts:**

- `trace_id`: Used for distributed tracing and log correlation across the system
- `parameters`: The actual inputs the tool needs to perform its action
- `metadata`: Optional contextual information (e.g., user_id, request_id)

### ToolResult

`ToolResult` represents the outcome of tool execution:

```python
class ToolResult:
    """Result of a tool execution."""
    
    ok: bool                        # True if execution succeeded
    data: dict[str, Any] | None     # Output payload on success
    error: dict[str, Any] | None    # Structured error information on failure
    trace_id: str                   # Same trace_id from ToolContext
```

**Success Path:**
```python
ToolResult(
    ok=True,
    data={"result": 42},
    error=None,
    trace_id="abc-123"
)
```

**Error Path:**
```python
ToolResult(
    ok=False,
    data=None,
    error={
        "code": "INVALID_INPUT",
        "message": "Parameter 'value' must be an integer",
        "retryable": False
    },
    trace_id="abc-123"
)
```

---

## Tool Lifecycle (Mental Model)

Understanding how Tools fit into the broader system helps you write better Tools.

### Execution Flow

```
┌─────────┐
│  Agent  │ ─── decides what to do
└────┬────┘
     │
     ▼
┌─────────────────┐
│  ToolRegistry   │ ─── locates and instantiates tool
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Tool.run()     │ ─── executes deterministic action
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│   ToolResult    │ ─── returns result to agent
└─────────────────┘
```

### Hard Boundaries

**What a Tool CAN access:**
- ✅ Input parameters via `ToolContext`
- ✅ Internal helper functions within the Tool class
- ✅ Injected dependencies (passed via constructor)
- ✅ Pure utility functions

**What a Tool CANNOT access:**
- ❌ The Agent that invoked it
- ❌ The ToolRegistry
- ❌ Other Tools directly
- ❌ Environment variables
- ❌ Global logging system (runtime handles logging)
- ❌ External APIs directly (use injected clients)

### Why These Boundaries Matter

These restrictions ensure:
- **Testability**: Tools can be tested in isolation
- **Predictability**: Same inputs always produce same outputs
- **Composability**: Tools can be combined without conflicts
- **Portability**: Tools work in any runtime environment

---

## Authoring Rules (Hard Rules)

These rules are **non-negotiable**. Violating them will cause integration failures or unpredictable behavior.

### ✅ MUST

1. **Produce deterministic output**
   - Same `ToolContext` → Same `ToolResult`
   - No random values, no timestamps, no system state dependencies
   - Example: Use trace_id from context, don't generate new UUIDs

2. **Always return ToolResult**
   - Never raise uncaught exceptions
   - Use `ok=False` with structured error for failures
   - Always propagate `trace_id` from context to result

3. **Validate input parameters internally**
   - Check for required parameters
   - Validate types and formats
   - Return explicit errors for invalid inputs
   - Don't assume parameters are pre-validated

4. **Return explicit errors**
   - Use structured error objects with `code`, `message`, `retryable`
   - Provide actionable error messages
   - Use UPPER_SNAKE_CASE for error codes

5. **Implement synchronous execution**
   - Tools run synchronously (async may come later)
   - Don't use async/await in tool implementation
   - Keep execution time short (< 5 seconds ideal)

### ❌ MUST NOT

1. **Use random or time-based output**
   ```python
   # ❌ BAD
   def run(self, context):
       return ToolResult(
           ok=True,
           data={"random": random.randint(1, 100)},  # Non-deterministic!
           trace_id=context.trace_id
       )
   ```

2. **Call external APIs directly**
   ```python
   # ❌ BAD
   def run(self, context):
       response = requests.get("https://api.example.com")  # Direct dependency!
       ...
   
   # ✅ GOOD - use injected client
   def __init__(self, api_client: APIClient):
       self.api_client = api_client
   
   def run(self, context):
       response = self.api_client.get("/data")  # Injected, testable
       ...
   ```

3. **Read environment variables directly**
   ```python
   # ❌ BAD
   def run(self, context):
       api_key = os.getenv("API_KEY")  # Tool shouldn't read env vars
       ...
   
   # ✅ GOOD - pass via constructor
   def __init__(self, api_key: str):
       self.api_key = api_key
   ```

4. **Raise uncaught exceptions**
   ```python
   # ❌ BAD
   def run(self, context):
       if context.parameters.get("value") is None:
           raise ValueError("value is required")  # Uncaught exception!
   
   # ✅ GOOD
   def run(self, context):
       if context.parameters.get("value") is None:
           return ToolResult(
               ok=False,
               error={
                   "code": "MISSING_PARAMETER",
                   "message": "Parameter 'value' is required",
                   "retryable": False
               },
               trace_id=context.trace_id
           )
   ```

5. **Import from Agent or Registry modules**
   ```python
   # ❌ BAD
   from packages.core.agents import AgentBase  # Creates circular dependency
   from packages.core.tools.registry import ToolRegistry  # Tight coupling
   ```

---

## Error Design Guidelines

Errors are a core part of the Tool contract. Well-designed errors enable proper error handling, retries, and debugging.

### Standard Error Shape

```json
{
  "code": "INVALID_INPUT",
  "message": "Parameter 'email' must be a valid email address",
  "retryable": false
}
```

### Error Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Machine-readable error code (UPPER_SNAKE_CASE) |
| `message` | string | Yes | Human-readable error description |
| `retryable` | boolean | Yes | Whether the operation can be retried |

### Error Code Conventions

**Format:** `UPPER_SNAKE_CASE`

**Categories:**

- `INVALID_INPUT` - Input validation failures
- `MISSING_PARAMETER` - Required parameter not provided
- `INVALID_FORMAT` - Parameter format is incorrect
- `OPERATION_FAILED` - General operation failure
- `EXTERNAL_SERVICE_ERROR` - External dependency failure (retryable)
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `PERMISSION_DENIED` - Authorization failure

### Retryable vs Non-retryable

**Retryable errors (`retryable: true`):**
- Transient network failures
- Rate limit exceeded
- Service temporarily unavailable
- Timeout errors

**Non-retryable errors (`retryable: false`):**
- Invalid input format
- Missing required parameter
- Permission denied
- Resource not found
- Logic errors

### Error Message Guidelines

**✅ GOOD:**
```python
{
    "code": "INVALID_INPUT",
    "message": "Parameter 'count' must be a positive integer, got: -5",
    "retryable": False
}
```

**❌ BAD:**
```python
{
    "code": "ERROR",
    "message": "Something went wrong",
    "retryable": False
}
```

**Best Practices:**
- Be specific about what went wrong
- Include the parameter name
- Show expected vs actual value when helpful
- Avoid generic messages like "error" or "failed"
- Don't expose internal implementation details
- Don't include sensitive data (passwords, tokens)

---

## Example: DummyTool (Reference)

`DummyTool` is the **canonical reference implementation** that demonstrates all Tool contract requirements.

### Location

```python
from packages.core.tools.examples import DummyTool
```

### What DummyTool Demonstrates

1. **Success Path**: Returns echoed input on valid parameters
2. **Error Path**: Returns structured error on invalid input
3. **Parameter Validation**: Checks for required parameters
4. **Trace ID Propagation**: Correctly passes trace_id through
5. **Deterministic Behavior**: Same input always produces same output
6. **Clean Interface**: Minimal, focused implementation

### Simplified Implementation

```python
class DummyTool(ToolBase):
    """
    Example tool that echoes input parameters.
    
    This is the canonical reference for tool implementation.
    """
    
    name = "dummy_tool"
    description = "Echoes input parameters for testing"
    version = "1.0.0"
    
    def run(self, context: ToolContext) -> ToolResult:
        """Execute the dummy tool."""
        
        # Validate required parameter
        if "message" not in context.parameters:
            return ToolResult(
                ok=False,
                data=None,
                error={
                    "code": "MISSING_PARAMETER",
                    "message": "Parameter 'message' is required",
                    "retryable": False
                },
                trace_id=context.trace_id
            )
        
        # Extract and echo parameter
        message = context.parameters["message"]
        
        # Return success result
        return ToolResult(
            ok=True,
            data={
                "echo": message,
                "tool_name": self.name
            },
            error=None,
            trace_id=context.trace_id
        )
```

### When to Reference DummyTool

- **Starting a new Tool**: Copy structure and adapt
- **Debugging issues**: Compare your Tool to DummyTool
- **Code reviews**: Check that new Tools follow DummyTool patterns
- **Learning**: Study DummyTool to understand best practices

---

## Testing a Tool

Every Tool must have tests that verify correct behavior in both success and failure scenarios.

### Minimum Required Tests

1. **Success case**: Tool executes successfully with valid input
2. **Error case**: Tool returns proper error with invalid input
3. **Serialization**: ToolResult can be serialized to JSON
4. **Deterministic behavior**: Multiple calls with same input produce same output

### Example Test Suite (pytest)

```python
import pytest
from packages.core.tools.examples import DummyTool
from packages.core.tools.schemas import ToolContext, ToolResult


class TestDummyTool:
    """Test suite for DummyTool."""
    
    def test_success_path(self):
        """Test tool execution with valid parameters."""
        tool = DummyTool()
        context = ToolContext(
            trace_id="test-123",
            parameters={"message": "hello"}
        )
        
        result = tool.run(context)
        
        assert result.ok is True
        assert result.data == {"echo": "hello", "tool_name": "dummy_tool"}
        assert result.error is None
        assert result.trace_id == "test-123"
    
    def test_missing_parameter(self):
        """Test tool returns error when required parameter is missing."""
        tool = DummyTool()
        context = ToolContext(
            trace_id="test-456",
            parameters={}
        )
        
        result = tool.run(context)
        
        assert result.ok is False
        assert result.data is None
        assert result.error is not None
        assert result.error["code"] == "MISSING_PARAMETER"
        assert result.error["retryable"] is False
        assert result.trace_id == "test-456"
    
    def test_result_serialization(self):
        """Test that ToolResult can be serialized to JSON."""
        tool = DummyTool()
        context = ToolContext(
            trace_id="test-789",
            parameters={"message": "world"}
        )
        
        result = tool.run(context)
        
        # If using Pydantic, this should work
        json_str = result.model_dump_json()
        assert "echo" in json_str
        assert "world" in json_str
    
    def test_deterministic_behavior(self):
        """Test that same input produces same output."""
        tool = DummyTool()
        context = ToolContext(
            trace_id="test-abc",
            parameters={"message": "test"}
        )
        
        result1 = tool.run(context)
        result2 = tool.run(context)
        
        assert result1.data == result2.data
        assert result1.ok == result2.ok
```

### Test Organization

```
tests/
  tools/
    test_dummy_tool.py
    test_calculator_tool.py
    test_email_validator_tool.py
```

### Testing Best Practices

- **Use fixtures** for common test data (ToolContext instances)
- **Test edge cases**: empty strings, null values, boundary conditions
- **Mock external dependencies**: Don't make real API calls in tests
- **Use parametrize** for testing multiple input combinations
- **Test error messages**: Verify error codes and messages are correct

---

## Tool Readiness Checklist

Before submitting a Tool for review or merging, verify all items:

### Implementation

- [ ] Tool inherits from or implements `ToolBase` interface
- [ ] Tool has `name`, `description`, and `version` attributes
- [ ] `run()` method accepts `ToolContext` and returns `ToolResult`
- [ ] All execution paths return `ToolResult` (no uncaught exceptions)
- [ ] Tool behavior is deterministic (no random values, timestamps, etc.)

### Input/Output

- [ ] Required parameters are validated
- [ ] Invalid input returns structured error with proper code
- [ ] Success result includes meaningful data
- [ ] `trace_id` is propagated from context to result
- [ ] Output can be serialized to JSON

### Dependencies

- [ ] No direct imports from Agent modules
- [ ] No direct imports from ToolRegistry modules
- [ ] No environment variable reads in `run()` method
- [ ] External dependencies are injected via constructor
- [ ] No direct API calls (use injected clients)

### Error Handling

- [ ] Errors use UPPER_SNAKE_CASE codes
- [ ] Error messages are clear and actionable
- [ ] `retryable` field is set correctly for each error type
- [ ] No sensitive data in error messages

### Testing

- [ ] Test file exists in `tests/tools/`
- [ ] Success path test included
- [ ] Error path test included
- [ ] Serialization test included
- [ ] Deterministic behavior test included
- [ ] All tests pass locally

### Documentation

- [ ] Tool has clear docstring explaining purpose
- [ ] Required parameters documented
- [ ] Return value documented
- [ ] Error codes documented

---

## Future Extensions (Non-binding)

These features are **not implemented yet**. Do not design your Tools around these features.

### Potential Future Features

1. **Async Tools**
   ```python
   async def run(self, context: ToolContext) -> ToolResult:
       ...
   ```
   - Enables I/O-bound operations
   - Requires runtime support for async execution

2. **Long-running Tools**
   - Background task execution
   - Progress reporting
   - Cancellation support

3. **Permission-aware Tools**
   ```python
   required_permissions = ["read:data", "write:data"]
   ```
   - Runtime checks permissions before execution
   - User/role-based access control

4. **Infra-backed Tools**
   - Tools that manage infrastructure resources
   - Deployment, scaling, monitoring tools

5. **Streaming Results**
   ```python
   def run(self, context: ToolContext) -> Iterator[ToolResult]:
       ...
   ```
   - For tools that produce incremental results
   - Useful for LLM text generation, large data processing

### Why Not Now?

These features add complexity without proven need. We implement them only when:
- Real use cases emerge
- Architecture can support them cleanly
- Tests and documentation are updated

**For now:** Focus on simple, synchronous, deterministic Tools.

---

## Out of Scope

This document **does not cover**:

### Tool Registry Internals
- How tools are registered
- How tools are discovered
- Tool versioning and compatibility
- Tool lifecycle management

**See:** `docs/TOOL_REGISTRY.md` (when available)

### Agent Selection Logic
- How agents choose which tool to use
- Tool recommendation algorithms
- Multi-tool orchestration

**See:** `docs/AGENTS.md` (when available)

### LLM Prompting
- How to describe tools to LLMs
- Tool calling formats for different LLM providers
- Prompt engineering for tool use

**See:** `docs/LLM_INTEGRATION.md` (when available)

### Memory / Context Merging
- How tool results are stored in agent memory
- Context window management
- Tool result summarization

**See:** `docs/AGENT_RUNTIME.md` (when available)

---

## Summary

Writing a Tool correctly means:

1. **Think deterministically**: Same input → Same output
2. **Follow the contract**: ToolBase → ToolContext → ToolResult
3. **Validate inputs**: Check parameters, return structured errors
4. **Stay isolated**: No agents, no registry, no global state
5. **Test thoroughly**: Success, error, serialization, determinism
6. **Reference DummyTool**: When in doubt, copy the pattern

**Remember:** Tools don't "think" — Tools only "do".

---

## Questions?

If this guide doesn't answer your question, or you find ambiguity:

1. Check the `DummyTool` implementation first
2. Review existing tool implementations for patterns
3. Ask in team chat or create a GitHub discussion
4. Propose updates to this document via PR

This guide evolves as we learn more about what works and what doesn't.
