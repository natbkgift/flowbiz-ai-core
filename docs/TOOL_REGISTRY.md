# Tool Registry v2

**Estimated reading time: 5 minutes**

## Overview

Tool Registry v2 is a lightweight, deterministic registry for managing tool specifications and their lifecycle. It provides a schema-first, contract-based approach to tool management without execution logic.

**What it is:**
- A registry for storing and managing tool metadata (specifications)
- An in-memory implementation with deterministic behavior
- A foundation for tool discovery, lifecycle management, and future extensions

**What it is NOT (yet):**
- A tool execution engine (execution comes in later phases)
- A permission enforcement system (permissions are contracts only)
- A persistent storage layer (no database, no files)

---

## Data Model

Tool Registry v2 uses three core schemas, all defined as immutable Pydantic models:

### ToolSpec

Defines the specification of a tool:

```python
ToolSpec(
    tool_name="weather_lookup",           # Required: unique identifier
    version="1.0.0",                      # Optional: version string
    description="Look up weather data",   # Optional: human-readable description
    input_schema={"city": "string"},      # Required: JSON-serializable input schema
    output_schema={"temp": "number"},     # Required: JSON-serializable output schema
    tags=["weather", "api"]               # Optional: list of tags for discovery
)
```

**Key characteristics:**
- `tool_name` is the unique key for registry lookups
- `input_schema` and `output_schema` are arbitrary JSON-serializable dicts
- All fields are immutable (frozen=True, extra="forbid")

### ToolRegistration

Represents a registered tool with runtime state:

```python
ToolRegistration(
    spec=ToolSpec(...),                   # The tool specification
    enabled=True,                         # Whether the tool is available
    created_at="2025-12-27T14:00:00Z"    # ISO8601 timestamp (optional)
)
```

**Key characteristics:**
- Wraps a `ToolSpec` with runtime state
- `enabled` flag controls availability (default: True)
- `created_at` is set automatically by the registry on registration

### ToolRegistrySnapshot

A snapshot of the entire registry state:

```python
ToolRegistrySnapshot(
    tools=[ToolRegistration(...), ...]   # List of all registrations
)
```

**Purpose:**
- Serialization and state transfer
- Testing and debugging
- Future persistence layer (when added)

---

## Lifecycle Operations

Tool Registry v2 supports the following operations:

### 1. Register

Register a tool with its specification:

```python
registry = InMemoryToolRegistry()
spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
registration = registry.register(spec)
```

**Registration rules:**
- If tool_name is new: creates a new registration with `enabled=True`
- If tool_name exists with identical spec: returns existing registration unchanged
- If tool_name exists with different version: overwrites with new registration
- If tool_name exists with same version but different spec: **raises ValueError**

**Rationale:** The last rule prevents accidental overwrites when the developer forgets to bump the version. If you want to update a tool's spec, you must update its version.

**Important edge case - Unversioned tools (version=None):**
When a tool is registered without a version (version=None), it cannot be updated with a different specification unless you first register it with an explicit version. This is because `None == None`, so both the existing and new specs are considered to have the "same version" (both unversioned). This behavior is by design to prevent accidental overwrites of unversioned tools.

**Example:**
```python
# Register unversioned tool
spec1 = ToolSpec(tool_name="example", version=None, input_schema={"a": "string"}, output_schema={})
registry.register(spec1)

# Attempt to update without version - will raise ValueError
spec2 = ToolSpec(tool_name="example", version=None, input_schema={"b": "number"}, output_schema={})
registry.register(spec2)  # ❌ Raises ValueError

# Solution: Add a version to update
spec3 = ToolSpec(tool_name="example", version="1.0.0", input_schema={"b": "number"}, output_schema={})
registry.register(spec3)  # ✅ Succeeds, overwrites with versioned spec
```

### 2. List All

List all registered tools (sorted by tool_name):

```python
# List only enabled tools
enabled_tools = registry.list_all()

# List all tools (including disabled)
all_tools = registry.list_all(include_disabled=True)
```

**Guarantees:**
- Results are always sorted by `tool_name` (ascending) for deterministic ordering
- By default, excludes disabled tools
- Stable results across repeated calls with same registry state

### 3. Get

Retrieve a specific tool by name:

```python
registration = registry.get("example")  # Returns ToolRegistration or None
```

### 4. Enable/Disable

Control tool availability:

```python
# Disable a tool
registry.set_enabled("example", enabled=False)

# Re-enable a tool
registry.set_enabled("example", enabled=True)
```

**Behavior:**
- Raises `KeyError` if tool_name is not registered
- Idempotent: calling with the same enabled state returns unchanged registration

### 5. Remove

Remove a tool from the registry:

```python
registry.remove("example")
```

**Behavior:**
- Idempotent: removing a non-existent tool succeeds silently
- No undo: once removed, the tool must be re-registered

---

## Determinism Guarantees

Tool Registry v2 is designed to be **fully deterministic** and **testable**:

1. **Stable ordering:** `list_all()` always returns tools sorted by `tool_name`
2. **No randomness:** No UUIDs, no random selection, no non-deterministic timestamps in tests
3. **No I/O:** No file system access, no database queries, no network calls
4. **No global state:** Each registry instance is independent
5. **Immutable contracts:** All schemas are frozen and forbid extra fields

**Why this matters:**
- Tests are stable and reproducible
- Results are predictable across environments
- No race conditions or concurrency issues (single-threaded use)
- Easy to snapshot and compare registry state

---

## Non-Goals (Intentionally Excluded)

The following are **not** part of Tool Registry v2 and will be addressed in future phases:

### Not Included

- **Tool execution:** Registry stores specs, not execution logic
- **Permission enforcement:** Permissions are defined as contracts but not enforced here
- **Persistence:** No database, no files, no state across process restarts
- **Async operations:** No background workers, no async/await
- **Network calls:** No external APIs, no webhooks
- **Subprocess management:** No shell commands, no tool sandboxing
- **Multi-tenancy:** No user/org isolation, no quotas
- **Web endpoints:** No HTTP routes exposed (that's the API layer's job)

### Why In-Memory First?

This is a deliberate architectural decision:

**ADR: Why In-Memory Implementation First?**

**Context:** Tool Registry v2 needs a simple, testable foundation that can be extended later.

**Decision:** Start with an in-memory implementation (no persistence) and add storage layers incrementally.

**Rationale:**
1. **Simplicity:** In-memory registries are trivial to test and reason about
2. **Fast iteration:** No schema migrations, no database setup, no connection pooling
3. **Clear contracts:** Forces us to design clean interfaces before adding complexity
4. **Plug-and-play:** The registry interface can be implemented with SQLite, PostgreSQL, or Redis later without changing consumer code
5. **Local development:** Developers can run tests and develop without external dependencies

**Consequences:**
- State is lost on process restart (acceptable for early phases)
- Not suitable for production multi-instance deployments (yet)
- Future work: Add persistent implementations (e.g., `SQLiteToolRegistry`, `PostgresToolRegistry`)

**Status:** Accepted for Phase P2-A (Core Runtime Foundation)

---

## Usage Examples

### Basic Registration

```python
from packages.core.tool_registry import InMemoryToolRegistry
from packages.core.contracts import ToolSpec

# Create registry
registry = InMemoryToolRegistry()

# Define a tool spec
spec = ToolSpec(
    tool_name="summarize_text",
    version="1.0.0",
    description="Summarize a text document",
    input_schema={"text": "string", "max_words": "number"},
    output_schema={"summary": "string"},
    tags=["nlp", "text"]
)

# Register the tool
registration = registry.register(spec)
print(f"Registered: {registration.spec.tool_name}")
```

### Listing Tools

```python
# List all enabled tools
for reg in registry.list_all():
    print(f"- {reg.spec.tool_name} (v{reg.spec.version}): {reg.spec.description}")

# List all tools (including disabled)
all_tools = registry.list_all(include_disabled=True)
print(f"Total tools: {len(all_tools)}")
```

### Enabling/Disabling

```python
# Disable a tool
registry.set_enabled("summarize_text", enabled=False)

# Verify it's excluded from default list
enabled_tools = registry.list_all()
assert not any(t.spec.tool_name == "summarize_text" for t in enabled_tools)

# But still present when including disabled
all_tools = registry.list_all(include_disabled=True)
assert any(t.spec.tool_name == "summarize_text" for t in all_tools)
```

### Version Updates

```python
# Register v1.0.0
spec_v1 = ToolSpec(
    tool_name="example",
    version="1.0.0",
    input_schema={},
    output_schema={}
)
registry.register(spec_v1)

# Update to v2.0.0 (allowed: different version)
spec_v2 = ToolSpec(
    tool_name="example",
    version="2.0.0",
    input_schema={"new_field": "string"},
    output_schema={}
)
registry.register(spec_v2)

# Attempting to re-register v2.0.0 with different spec raises ValueError
spec_v2_modified = ToolSpec(
    tool_name="example",
    version="2.0.0",  # Same version!
    input_schema={"different_field": "number"},  # Different schema!
    output_schema={}
)
try:
    registry.register(spec_v2_modified)
except ValueError as e:
    print(f"Error: {e}")  # Expected!
```

---

## Testing

Tool Registry v2 includes comprehensive tests in `tests/test_tool_registry.py`:

- **Round-trip serialization:** Verify contracts serialize/deserialize correctly
- **Immutability:** Verify frozen models reject mutations
- **Registration logic:** Verify version-based overwrite rules
- **Sorting:** Verify `list_all()` produces stable, sorted results
- **Enable/disable:** Verify state changes work correctly
- **Error handling:** Verify expected exceptions for unknown tools
- **Idempotency:** Verify `remove()` and duplicate registrations behave correctly

Run tests with:

```bash
pytest tests/test_tool_registry.py -v
```

---

## Future Extensions

Tool Registry v2 is designed to be extended in future phases:

1. **Persistence layer:** Add `SQLiteToolRegistry`, `PostgresToolRegistry`
2. **Tool execution:** Add execution engine that uses registry to discover tools
3. **Permission enforcement:** Add runtime checks using permission contracts
4. **Search/discovery:** Add tag-based search, full-text search on descriptions
5. **Versioning:** Add semantic version comparison and deprecation support
6. **Webhooks:** Add event hooks for registration/removal (observability)
7. **Multi-tenancy:** Add user/org scoping for isolated registries

**Principle:** Add complexity incrementally, always maintaining backward compatibility.

---

## Summary

Tool Registry v2 provides:
- ✅ Schema-first contracts for tool specifications
- ✅ Deterministic, testable in-memory implementation
- ✅ Lifecycle management (register, enable/disable, list, remove)
- ✅ Clear non-goals and future extension points
- ✅ Comprehensive tests and documentation

**Read time: ~5 minutes** ✅

For questions or clarifications, open an issue or propose an ADR.
