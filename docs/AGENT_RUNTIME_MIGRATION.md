# Agent Runtime Migration Guide

This guide helps developers migrate from the legacy agent runtime to the new runtime system.

## Overview

FlowBiz AI Core has **two agent runtime implementations**:

- **✅ New Runtime** (`packages.core.runtime`) - **Recommended for all new code**
- **⚠️ Legacy Runtime** (`packages.core.agents`) - **Deprecated, maintained for compatibility**

## Key Differences

| Aspect | Legacy Runtime | New Runtime (Recommended) |
|--------|---------------|-------------------------|
| **Location** | `packages.core.agents` | `packages.core.runtime` |
| **Agent Interface** | `AgentBase.run(AgentContext) -> AgentResult` | `AgentBase.execute(RuntimeContext) -> RuntimeResult` |
| **Agent Management** | Single agent per runtime instance | Built-in agent registry (`_agents` dict) |
| **Agent Selection** | Fixed at runtime creation | Dynamic by name from request |
| **Error Handling** | Basic string-based status | Structured `RuntimeError` objects |
| **Endpoints** | `/v1/agent/run/legacy` | `/v1/agent/run` |
| **Status** | Deprecated ⚠️ | Active development ✅ |

## Migration Steps

### 1. Update Imports

**Before (Legacy):**
```python
from packages.core.agents import AgentBase, AgentContext, AgentResult, AgentRuntime
```

**After (New):**
```python
from packages.core.runtime import AgentBase, RuntimeContext, RuntimeResult, AgentRuntime
```

### 2. Update Agent Interface

**Before (Legacy):**
```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
    
    def run(self, ctx: AgentContext) -> AgentResult:
        return AgentResult(
            output_text=f"Processed: {ctx.input_text}",
            status="ok",
            reason=None,
            trace={"agent_name": self.name}
        )
```

**After (New):**
```python
class MyAgent(AgentBase):
    def __init__(self):
        super().__init__(name="my-agent")
    
    def execute(self, ctx: RuntimeContext) -> RuntimeResult:
        return RuntimeResult(
            status="ok",
            trace_id=ctx.trace_id,
            agent=self.name,
            output=f"Processed: {ctx.input}",
            errors=[]
        )
```

### 3. Update Runtime Usage

**Before (Legacy):**
```python
# Single agent per runtime
runtime = AgentRuntime(agent=MyAgent())
result = runtime.run(
    input_text="hello",
    request_id="req-123",
    user_id="user-456"
)
```

**After (New):**
```python
# Agent registry approach
runtime = AgentRuntime()
# Register your agent (or use built-in ones like "echo")
runtime._agents["my-agent"] = MyAgent()

ctx = RuntimeContext(
    agent="my-agent",
    input="hello", 
    trace_id="req-123"
)
result = runtime.run(ctx)
```

### 4. Update API Calls

**Before (Legacy):**
```bash
curl -X POST /v1/agent/run/legacy \
  -H "Content-Type: application/json" \
  -d '{"input_text": "hello", "user_id": "user-123"}'
```

**After (New):**
```bash
curl -X POST /v1/agent/run \
  -H "Content-Type: application/json" \
  -d '{"agent": "echo", "input": "hello", "meta": {"trace_id": "req-123"}}'
```

## Response Format Differences

### Legacy Runtime Response
```json
{
  "output_text": "OK: hello",
  "status": "ok",
  "reason": null,
  "trace": {
    "agent_name": "default",
    "request_id": "req-123"
  }
}
```

### New Runtime Response
```json
{
  "status": "ok",
  "trace_id": "req-123", 
  "agent": "echo",
  "output": "hello",
  "errors": []
}
```

## Recommendations

1. **New Projects**: Use the new runtime (`packages.core.runtime`) exclusively
2. **Existing Projects**: Gradually migrate to the new runtime when convenient
3. **Legacy Support**: The legacy runtime will be maintained for backward compatibility but won't receive new features
4. **Testing**: Both systems are fully tested and production-ready

## Questions?

- Check the [Architecture documentation](ARCHITECTURE.md) for detailed technical information
- See the [Tool Authoring Guide](TOOLS.md) for tool-related runtime usage
- Review the implementation in `packages/core/runtime/` for examples

---

**Migration Status**: The new runtime is stable and recommended for all new development. Legacy runtime is deprecated but supported.