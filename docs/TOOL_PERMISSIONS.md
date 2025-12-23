# Tool Permissions Model

**Status:** Design-only (no runtime enforcement)  
**Phase:** Phase 2 — AI Hub Core (Foundation / Design)  
**Depends on:** PR-023, PR-023.1, PR-023.2

---

## Overview

This document defines the **permission model** for Tools and Agent Personas in FlowBiz AI Core. The model establishes a deny-by-default, least-privilege framework that will guide future implementation work in the Tool Registry (PR-024) and Execution Pipeline (PR-030).

**Important:** This is a **design-only** document. No runtime enforcement is implemented yet. The types and schemas defined here serve as contracts for future work.

## Contracts (Tool / Persona / Authorize Hook)

The permission model is captured as **pure schemas and a stubbed hook**—no runtime enforcement today. Tool and persona authors can start declaring intent using the following contracts:

```python
from packages.core.tools import AgentPolicy, Permission, ToolPermissions, authorize


class ExampleTool:
    """Pseudo-tool showing permission declaration (design-only)."""

    permissions = ToolPermissions(
        required_permissions=[Permission.READ_FS],
        optional_permissions=[Permission.NET_HTTP],
    )


persona_policy = AgentPolicy(
    persona="core",
    allowed_permissions=[Permission.READ_FS, Permission.NET_HTTP],
    allowed_tools=["example_tool"],
)

# Future (PR-030): the execution pipeline will call authorize(...) before run()
decision = authorize(tool=ExampleTool(), ctx=None, policy=persona_policy)
```

- `ToolPermissions`: what a tool says it needs (required + optional).
- `AgentPolicy`: what a persona allows (permissions + optional tool allowlist).
- `authorize(...)`: contract-only hook that will be invoked in PR-030 before execution.

---

## 1. Terminology

### Tool
A deterministic capability that performs a specific action. Tools are units of work that execute operations like reading files, making HTTP requests, or running shell commands. Tools declare what permissions they need to function.

### Permission
A capability or privilege that a Tool requires to execute its function. Permissions represent access to resources or operations (e.g., `READ_FS`, `NET_HTTP`, `EXEC_SHELL`). Tools declare their permission requirements; the system enforces whether those permissions are granted.

### Persona
An agent category or role that defines what an agent is allowed to do. Personas group agents with similar trust levels and operational boundaries. Examples: `core` (business logic), `infra` (infrastructure management), `docs` (documentation work).

### Policy
A set of rules that determines whether a Tool can be executed by an agent with a given Persona. Policies map Personas to allowed permissions and optionally to specific allowed Tools. The policy decision engine (future) uses these rules to authorize or deny tool execution.

---

## 2. Core Principles

The permission model is built on these foundational principles:

### Deny by Default
If a Tool requests a permission that is not explicitly allowed for the agent's Persona, execution is **denied**. No implicit grants, no fallback to "allow". Safety through explicit authorization.

### Least Privilege
Agents and Tools should operate with the **minimum** permissions necessary to accomplish their tasks. Broad permissions (e.g., `EXEC_SHELL`) should be granted only when absolutely required and with clear justification.

### Tool Declares What It Needs
Tools explicitly declare their permission requirements through `required_permissions` and `optional_permissions`. This makes tool capabilities transparent and auditable. The tool author knows best what resources the tool needs.

### Agent Persona Decides What Is Allowed
Each Persona has an `allowed_permissions` set that defines the upper bound of what any tool can request when invoked by that agent. Personas can also specify an `allowed_tools` allowlist for tighter control.

### Runtime Enforcement Is a Future Concern
This design establishes the schema, vocabulary, and decision rules. Actual enforcement (authorization checks before `tool.run()`) will be implemented in PR-030 (Execution Pipeline). For now, these are purely declarative contracts.

---

## 3. 2-Layer Permission Model

The permission model has two layers: **Tool side** (what capabilities a tool needs) and **Persona side** (what capabilities an agent is allowed to use).

### Tool Side: Permission Requirements

Tools declare their permission needs using two fields:

#### `required_permissions`
A list of permissions the Tool **must have** to function correctly. If any required permission is denied, the tool cannot execute.

**Example:**
```python
required_permissions = [Permission.READ_FS, Permission.NET_HTTP]
```

This tool cannot run without filesystem read access AND network HTTP access.

#### `optional_permissions`
A list of permissions the Tool can **use if available**, but can function without. These enable enhanced behavior when granted, but their absence doesn't prevent execution.

**Example:**
```python
optional_permissions = [Permission.WRITE_FS]
```

This tool can optionally write results to disk if allowed, but will work fine without it.

### Persona Side: Permission Allowances

Personas define what permissions agents in that category are allowed to use:

#### `allowed_permissions`
A list of permissions that agents with this Persona can grant to Tools. This is the **authorization boundary** for the agent.

**Example:**
```python
allowed_permissions = [Permission.NET_HTTP, Permission.READ_ENV]
```

Agents with this Persona can only invoke tools that require `NET_HTTP` or `READ_ENV` (or both). Any tool requesting other permissions will be denied.

#### `allowed_tools` (Optional Allowlist)
An optional list of specific tool names that agents with this Persona are allowed to execute. When set, this provides an additional constraint: even if permissions match, the tool name must be in the allowlist.

**Example:**
```python
allowed_tools = ["web_search", "fetch_api", "validate_url"]
```

Even if a tool's permissions are satisfied, it can only run if its name is in this list.

### Future Decision Rule

When a Tool is about to execute, the authorization system (future, PR-030) will apply this logic:

```
IF (tool.required_permissions ⊆ persona.allowed_permissions)
   AND (allowed_tools is empty OR tool.name IN allowed_tools)
THEN
   ALLOW execution
ELSE
   DENY execution
```

**Note:** Optional permissions can be partially granted or denied without blocking execution.

**Key Points:**
- All `required_permissions` must be satisfied
- `optional_permissions` can be partially granted or denied without blocking execution
- If `allowed_tools` is specified, the tool name must match
- Missing permissions result in explicit denial

---

## 4. Permission Set (Initial)

The following permissions represent the initial capability set. This list is intentionally minimal and can be extended as new tool requirements emerge.

### File System Permissions

#### `READ_FS`
Read access to the filesystem. Allows tools to read file contents, list directories, check file existence.

**Use cases:** Configuration loaders, documentation parsers, log analyzers

#### `WRITE_FS`
Write access to the filesystem. Allows tools to create, modify, or delete files and directories.

**Use cases:** Code generators, report writers, documentation updaters

### Network Permissions

#### `NET_HTTP`
HTTP/HTTPS network access. Allows tools to make outbound HTTP requests to external services.

**Use cases:** API clients, web scrapers, webhook callers, external data fetchers

### Execution Permissions

#### `EXEC_SHELL`
Shell command execution. Allows tools to run arbitrary shell commands on the host system.

**Use cases:** Build tools, deployment scripts, system diagnostics

**⚠️ High Risk:** This permission grants significant control and should be restricted to trusted personas only.

### Environment Permissions

#### `READ_ENV`
Read access to environment variables. Allows tools to read configuration and secrets from the environment.

**Use cases:** Configuration readers, credential fetchers, feature flag checkers

### Database Permissions

#### `DB_READ`
Read access to databases. Allows tools to execute SELECT queries and read data.

**Use cases:** Data analytics tools, report generators, search interfaces

#### `DB_WRITE`
Write access to databases. Allows tools to execute INSERT, UPDATE, DELETE queries.

**Use cases:** Data migration tools, CRUD operations, data import pipelines

**⚠️ High Risk:** This permission can modify persistent state and should be carefully controlled.

---

## 5. Persona Examples (MVP)

The following personas represent the minimal viable set for Phase 2. Each persona has a distinct trust level and operational scope.

| Persona | Allowed Permissions | Notes |
|---------|---------------------|-------|
| `core` | `NET_HTTP`, `READ_ENV` | Business logic agents. Can make API calls and read configuration. **Cannot** write files or execute shell commands. Safe for production workflows. |
| `infra` | `NET_HTTP`, `EXEC_SHELL`, `READ_FS`, `WRITE_FS` | Infrastructure management agents. Can deploy, configure, and manage system resources. **Path restrictions should be added later** to limit filesystem scope. Requires elevated trust. |
| `docs` | `READ_FS`, `WRITE_FS` | Documentation agents. Can read and write documentation files. **Scoped to `docs/` directory only** (future enforcement). **Cannot** access network or execute shell commands. Safe for content work. |

### Design Rationale

**`core` persona:**
- Most restrictive by default
- Suitable for customer-facing business logic
- Network access for API integrations (common need)
- No filesystem write to prevent unintended modifications
- No shell execution to prevent security risks

**`infra` persona:**
- Elevated privileges for system management
- Shell execution needed for deployments and diagnostics
- Filesystem access for configuration and logs
- Should be restricted to infrastructure agents only
- Future: add path-based restrictions

**`docs` persona:**
- Isolated from network and execution
- Safe for community contributors and doc agents
- Can read existing docs and write new content
- Future: enforce directory scope to prevent access outside `docs/`

---

## 6. Example Policy (Illustrative)

The following YAML-like structure illustrates what a policy definition might look like. This is **NOT parsed or enforced** in this PR. It serves as a reference for future implementation.

### Example 1: Core Agent Policy

```yaml
persona: core
allowed_permissions:
  - NET_HTTP
  - READ_ENV
allowed_tools:
  - web_search
  - fetch_api
  - validate_email
  - format_json
```

**Interpretation:**
- Agents with `core` persona can use tools requiring `NET_HTTP` or `READ_ENV`
- Only the four listed tools are executable (allowlist enforced)
- Any tool requesting `WRITE_FS`, `EXEC_SHELL`, etc. will be denied
- Any tool not in `allowed_tools` will be denied, even if permissions match

### Example 2: Infra Agent Policy

```yaml
persona: infra
allowed_permissions:
  - NET_HTTP
  - EXEC_SHELL
  - READ_FS
  - WRITE_FS
  - READ_ENV
allowed_tools: []  # Empty = all tools allowed (if permissions match)
```

**Interpretation:**
- Agents with `infra` persona have broad permissions
- Can execute shell commands and modify filesystem
- No tool allowlist, so any tool can run if permissions are satisfied
- Suitable for trusted infrastructure automation

### Example 3: Docs Agent Policy

```yaml
persona: docs
allowed_permissions:
  - READ_FS
  - WRITE_FS
allowed_tools:
  - markdown_lint
  - spell_check
  - generate_toc
  - update_readme
```

**Interpretation:**
- Agents with `docs` persona are isolated from network and execution
- Can read and write files (future: enforce path restrictions)
- Only documentation-related tools are allowed
- Safe for community contributions

### Example 4: Tool Requiring Optional Permission

```yaml
# Tool definition (not policy, but shows interaction)
tool:
  name: data_exporter
  required_permissions:
    - DB_READ
  optional_permissions:
    - WRITE_FS  # If allowed, writes to disk; otherwise returns data inline
```

**Behavior:**
- Tool **requires** `DB_READ` to function
- Tool will **use** `WRITE_FS` if available, but can work without it
- If run by `core` agent (no `WRITE_FS`), tool runs but doesn't write files
- If run by `infra` agent (has `WRITE_FS`), tool runs and writes files

---

## 7. Future Hook (Non-binding)

This section describes the **future integration point** for runtime enforcement. This is **NOT implemented** in this PR.

### Call Site

Before executing a tool, the Execution Pipeline (PR-030) will call an authorization function:

```python
# Future implementation in PR-030
def execute_tool(tool: ToolBase, context: ToolContext, tool_permissions: ToolPermissions, agent_policy: AgentPolicy) -> ToolResult:
    """Execute a tool with authorization check."""
    
    # FUTURE: Authorization hook
    decision = authorize(tool, tool_permissions, agent_policy)
    
    if not decision.allowed:
        return ToolResult(
            ok=False,
            data=None,
            error=ToolError(
                code="PERMISSION_DENIED",
                message=decision.reason,
                retryable=False
            ),
            trace_id=context.trace_id,
            tool_name=tool.name
        )
    
    # If authorized, execute
    return tool.run(context)
```

### Authorization Function (Future)

```python
# Future implementation in PR-030 or later
def authorize(tool: ToolBase, tool_permissions: ToolPermissions, policy: AgentPolicy) -> PolicyDecision:
    """
    Determine if a tool can be executed under the given policy.
    
    Args:
        tool: The tool requesting execution
        tool_permissions: Permission requirements for the tool
        policy: The agent's permission policy
        
    Returns:
        PolicyDecision indicating allowed/denied and reason
    """
    # Check tool allowlist (if specified)
    if policy.allowed_tools and tool.name not in policy.allowed_tools:
        return PolicyDecision(
            allowed=False,
            reason=f"Tool '{tool.name}' not in allowed_tools list"
        )
    
    # Check required permissions
    missing = set(tool_permissions.required_permissions) - set(policy.allowed_permissions)
    
    if missing:
        return PolicyDecision(
            allowed=False,
            reason=f"Missing required permissions: {missing}"
        )
    
    # All checks passed
    return PolicyDecision(
        allowed=True,
        reason="All required permissions satisfied"
    )
```

### Integration Points

The authorization hook will be integrated at these locations (future):

1. **Tool Registry:** When a tool is retrieved, attach policy context
2. **Execution Pipeline:** Before `tool.run()`, call `authorize()`
3. **Agent Runtime:** Pass agent policy to execution pipeline

### Clearly Labeled as Future-Only

⚠️ **This authorization logic is NOT implemented yet.**

The schemas and types defined in `packages/core/tools/permissions.py` provide the contracts, but enforcement is deferred to PR-030. Until then:

- Tools can declare permissions but they are not checked
- Policies can be defined but they are not enforced  
- The `authorize()` function does not exist yet

This design serves as the blueprint for implementation.

---

## Summary

This permission model provides a clear, extensible framework for securing tool execution:

1. **Tools declare** what they need (`required_permissions`, `optional_permissions`)
2. **Personas define** what agents can use (`allowed_permissions`, `allowed_tools`)
3. **Policies enforce** the rules (future: PR-030)
4. **Deny by default** ensures safety
5. **Least privilege** minimizes risk

By establishing this design now, we ensure that Tool Registry v2 (PR-024) and Execution Pipeline (PR-030) have a clear, consistent model to implement.

---

## Next Steps

After this PR merges:

1. **PR-024:** Tool Registry v2 will read and store `required_permissions` and `optional_permissions` from tool metadata
2. **PR-030:** Execution Pipeline will implement the `authorize()` function and enforce policies before tool execution
3. **Future:** Path-based restrictions (e.g., `docs` persona limited to `docs/` directory), audit logging, dynamic policy updates

For questions or proposed changes to this model, open a GitHub discussion or submit a PR with clear rationale.
