# Tool Permission Examples

**Status:** Examples and guidelines only (NOT ENFORCED)  
**Phase:** Phase 2 — AI Hub Core  
**Depends on:** PR-023, PR-023.1, PR-023.2, PR-023.4

---

## 1. Purpose

This document provides **practical examples and guidelines** for declaring permissions in Tools.

### What This Document IS

- ✅ A reference guide for tool authors showing permission declaration patterns
- ✅ A collection of examples demonstrating tool category → permission mapping
- ✅ A set of best practices and anti-patterns to improve consistency
- ✅ A resource to speed up code reviews by making intent explicit

### What This Document IS NOT

- ❌ **NOT an enforced rule set** — no CI checks validate these examples
- ❌ **NOT runtime enforcement** — permissions are not checked during execution
- ❌ **NOT a policy engine** — authorization logic is not implemented yet

### Goal

The goal is to establish **consistency and clarity** from day one:

- **Tool authors** don't need to guess what permissions to declare
- **Reviewers** can quickly verify that declared permissions match tool behavior
- **Future PRs** (PR-024 Tool Registry, PR-030 Execution Pipeline) can integrate smoothly by reading declared permissions

By declaring permissions explicitly now, we:
- **Prevent privilege creep** (tools asking for more than they need)
- **Improve auditability** (clear record of what each tool can do)
- **Enable future enforcement** (runtime can read and enforce permissions later)

---

## 2. Tool Category → Permission Mapping

This table maps common tool categories to their typical permission requirements. Use this as a reference when designing new tools.

| Tool Category | Required Permissions | Optional Permissions | Notes |
|---------------|---------------------|---------------------|-------|
| **HTTP / API Tool** | `NET_HTTP` | `READ_ENV` | For making external HTTP requests. May need `READ_ENV` for API keys via config layer. |
| **File Read Tool** | `READ_FS` | — | Read-only filesystem access. Examples: log parsers, config readers, documentation indexers. |
| **File Write Tool** | `READ_FS`, `WRITE_FS` | — | Requires both read and write for most use cases. Examples: code generators, report writers. |
| **Shell / System Tool** | `EXEC_SHELL` | `READ_FS`, `WRITE_FS` | **High risk** — should be infra-persona only. Often needs filesystem access for scripts. |
| **Environment Reader** | `READ_ENV` | — | **Must use config abstraction layer**, not direct `os.environ`. For feature flags, settings. |
| **Database Read Tool** | `DB_READ` | — | Read-only database access. For analytics, reporting, search queries. |
| **Database Write Tool** | `DB_READ`, `DB_WRITE` | — | **Explicit only** — never grant by default. For migrations, CRUD operations, data imports. |
| **Pure Computation** | — | — | No permissions needed. For validation, formatting, calculations, transformations. |

### Key Principles

1. **Deny by default** — if a tool doesn't need a permission, don't declare it
2. **Least privilege** — declare the minimum permissions needed to function
3. **Be explicit** — don't assume reviewers know what your tool does
4. **Separate read/write** — don't ask for `WRITE_FS` if you only read files

---

## 3. Example Tools

Below are **5–8 illustrative examples** showing how different tool types should declare permissions.

### Example 1: HTTP Fetch Tool

**Use case:** Fetch data from an external API endpoint

**Permissions:**
- **Required:** `NET_HTTP` (outbound HTTP requests only)
- **Optional:** None

**Rationale:**
- Tool makes external HTTP calls to fetch data
- No filesystem or database access needed
- No environment variable reads (API keys passed via config layer)

```python
class HTTPFetchTool(ToolBase):
    name = "http_fetch"
    description = "Fetch data from external HTTP APIs"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.NET_HTTP],
        optional_permissions=[],
    )
```

---

### Example 2: Documentation Generator Tool

**Use case:** Read source files and generate documentation

**Permissions:**
- **Required:** `READ_FS`, `WRITE_FS`
- **Optional:** None

**Rationale:**
- Reads source code files to extract documentation
- Writes generated markdown files to docs directory
- No network, no execution, no environment access
- Safe for docs persona agents

```python
class DocsGeneratorTool(ToolBase):
    name = "docs_generator"
    description = "Generate documentation from source code"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.READ_FS, Permission.WRITE_FS],
        optional_permissions=[],
    )
```

---

### Example 3: Infrastructure Diagnostics Tool

**Use case:** Run system commands to check infrastructure health

**Permissions:**
- **Required:** `EXEC_SHELL`, `READ_FS`
- **Optional:** `WRITE_FS`

**Rationale:**
- Executes shell commands (`df`, `free`, `ps`) to gather metrics
- Reads log files and config files for diagnostics
- Optionally writes diagnostic reports to disk
- **Infra persona only** due to `EXEC_SHELL` privilege

```python
class InfraDiagnoseTool(ToolBase):
    name = "infra_diagnose"
    description = "Run infrastructure health diagnostics"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.EXEC_SHELL, Permission.READ_FS],
        optional_permissions=[Permission.WRITE_FS],
    )
```

---

### Example 4: Configuration Reader Tool

**Use case:** Read application configuration values

**Permissions:**
- **Required:** `READ_ENV`
- **Optional:** None

**Rationale:**
- Reads configuration via config abstraction layer
- **Must NOT use `os.environ` directly** — use config layer
- No filesystem, network, or execution access
- Safe for core persona agents

```python
class ConfigReaderTool(ToolBase):
    name = "config_reader"
    description = "Read application configuration settings"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.READ_ENV],
        optional_permissions=[],
    )
```

---

### Example 5: Database Export Tool

**Use case:** Export data from database to CSV file

**Permissions:**
- **Required:** `DB_READ`, `WRITE_FS`
- **Optional:** None

**Rationale:**
- Reads data from database via SELECT queries
- Writes results to filesystem as CSV
- No network or execution access
- Appropriate for analytics/reporting workflows

```python
class DatabaseExportTool(ToolBase):
    name = "database_export"
    description = "Export database query results to CSV"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.DB_READ, Permission.WRITE_FS],
        optional_permissions=[],
    )
```

---

### Example 6: Email Validator Tool

**Use case:** Validate email address format (pure computation)

**Permissions:**
- **Required:** None
- **Optional:** None

**Rationale:**
- Pure validation logic — no external resources
- No network, filesystem, database, or execution
- Can run in any persona without risk
- Safe for all agents

```python
class EmailValidatorTool(ToolBase):
    name = "email_validator"
    description = "Validate email address format"
    
    permissions = ToolPermissions(
        required_permissions=[],
        optional_permissions=[],
    )
```

---

### Example 7: Web Scraper Tool

**Use case:** Fetch and parse web pages

**Permissions:**
- **Required:** `NET_HTTP`
- **Optional:** `WRITE_FS`

**Rationale:**
- Makes HTTP requests to fetch web content
- Parses and extracts data from HTML
- Optionally caches results to disk
- Works without cache if `WRITE_FS` denied

```python
class WebScraperTool(ToolBase):
    name = "web_scraper"
    description = "Scrape and parse web content"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.NET_HTTP],
        optional_permissions=[Permission.WRITE_FS],
    )
```

---

### Example 8: Deployment Tool

**Use case:** Deploy application to production environment

**Permissions:**
- **Required:** `EXEC_SHELL`, `READ_FS`, `NET_HTTP`
- **Optional:** `WRITE_FS`, `READ_ENV`

**Rationale:**
- Executes deployment scripts and commands
- Reads deployment configurations and manifests
- Makes HTTP calls to deployment APIs
- Optionally writes deployment logs
- **Infra persona only** — highest privilege level

```python
class DeploymentTool(ToolBase):
    name = "deployment"
    description = "Deploy application to production"
    
    permissions = ToolPermissions(
        required_permissions=[
            Permission.EXEC_SHELL,
            Permission.READ_FS,
            Permission.NET_HTTP,
        ],
        optional_permissions=[Permission.WRITE_FS, Permission.READ_ENV],
    )
```

---

## 4. Example Code (Illustrative)

Below is a **complete example** showing how to declare permissions in a Tool implementation.

### Full Example: DummyTool with Permissions

```python
"""DummyTool with permission declaration example."""

from packages.core.tools.base import ToolBase
from packages.core.tools.context import ToolContext
from packages.core.tools.result import ToolResult, ToolError
from packages.core.tools.permissions import ToolPermissions, Permission


class DummyTool(ToolBase):
    """
    Example tool demonstrating permission declaration.
    
    This tool echoes input parameters back to the caller.
    It requires no special permissions as it performs pure computation.
    """
    
    @property
    def name(self) -> str:
        return "dummy.echo"
    
    @property
    def description(self) -> str:
        return "Echo back provided params for testing and examples"
    
    @property
    def version(self) -> str:
        return "v1"
    
    @property
    def permissions(self) -> ToolPermissions:
        """
        Declare this tool's permission requirements.
        
        DummyTool performs pure computation (echo) with no external access,
        so it requires no permissions.
        """
        return ToolPermissions(
            required_permissions=[],  # No permissions needed
            optional_permissions=[],
        )
    
    def run(self, context: ToolContext) -> ToolResult:
        """Execute the dummy echo tool."""
        # Implementation remains unchanged
        if not isinstance(context.params, dict):
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    code="INVALID_PARAMS",
                    message="Params must be a dictionary",
                    retryable=False,
                ),
                trace_id=context.trace_id,
                tool_name=self.name,
            )
        
        if not context.params:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    code="EMPTY_PARAMS",
                    message="No params provided",
                    retryable=False,
                ),
                trace_id=context.trace_id,
                tool_name=self.name,
            )
        
        return ToolResult(
            ok=True,
            data={"echoed": context.params},
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )
```

### Important Notes on This Example

⚠️ **This permission declaration is EXAMPLE-ONLY and NOT ENFORCED YET**

- The `permissions` property is **not validated** by the runtime
- Tools can run **without** declaring permissions (for now)
- Future PRs (PR-024, PR-030) will integrate permission checks
- Declaring permissions now makes future integration seamless

### Alternative Declaration Styles

You can also declare permissions as a class attribute:

```python
class ExampleTool(ToolBase):
    """Alternative style using class attribute."""
    
    name = "example"
    description = "Example tool"
    
    # Class attribute style
    permissions = ToolPermissions(
        required_permissions=[Permission.NET_HTTP],
        optional_permissions=[],
    )
    
    def run(self, context: ToolContext) -> ToolResult:
        ...
```

Both styles (property vs class attribute) are acceptable. Use whichever fits your tool's design.

---

## 5. Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Direct Environment Variable Access

**Problem:** Tool reads `os.environ` directly instead of using config layer

```python
# ❌ BAD — violates abstraction
import os

class BadConfigTool(ToolBase):
    def run(self, context: ToolContext) -> ToolResult:
        api_key = os.environ.get("API_KEY")  # Direct env access
        ...
```

**Why it's wrong:**
- Bypasses config abstraction layer
- Makes testing difficult (need to set env vars)
- Permission declaration (`READ_ENV`) has no meaning
- Cannot be controlled by authorization system

**✅ Fix:** Use config layer and declare `READ_ENV`

```python
# ✅ GOOD — uses config abstraction
class GoodConfigTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[Permission.READ_ENV],
    )
    
    def __init__(self, config: ConfigService):
        self.config = config  # Injected dependency
    
    def run(self, context: ToolContext) -> ToolResult:
        api_key = self.config.get("API_KEY")  # Via config layer
        ...
```

---

### ❌ Anti-Pattern 2: Over-Privileged Tool

**Problem:** Tool requests `EXEC_SHELL` when it only needs HTTP access

```python
# ❌ BAD — over-privileged
class BadHTTPTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[
            Permission.EXEC_SHELL,  # Why? Not needed!
            Permission.NET_HTTP,
            Permission.WRITE_FS,    # Also not needed!
        ],
    )
```

**Why it's wrong:**
- Requests unnecessary privileges
- Increases attack surface if tool is compromised
- Violates least privilege principle
- Makes reviewers question tool safety

**✅ Fix:** Request only what's needed

```python
# ✅ GOOD — minimal permissions
class GoodHTTPTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[Permission.NET_HTTP],  # Only what's needed
    )
```

---

### ❌ Anti-Pattern 3: Missing Permission Declaration

**Problem:** Tool doesn't declare permissions at all

```python
# ❌ BAD — no permission declaration
class BadNoPermsTool(ToolBase):
    name = "bad_tool"
    description = "Does file operations"
    
    def run(self, context: ToolContext) -> ToolResult:
        with open("/tmp/data.txt", "w") as f:  # Writes files!
            f.write("data")
        ...
```

**Why it's wrong:**
- Reviewers must read implementation to understand capabilities
- Future authorization system cannot enforce policy
- Intent is not explicit
- Makes permission audits impossible

**✅ Fix:** Always declare permissions

```python
# ✅ GOOD — explicit permission declaration
class GoodFileTool(ToolBase):
    name = "good_tool"
    description = "Writes data files"
    
    permissions = ToolPermissions(
        required_permissions=[Permission.WRITE_FS],
    )
    
    def run(self, context: ToolContext) -> ToolResult:
        with open("/tmp/data.txt", "w") as f:
            f.write("data")
        ...
```

---

### ❌ Anti-Pattern 4: Confusing Required vs Optional

**Problem:** Tool declares required permission as optional (or vice versa)

```python
# ❌ BAD — DB_READ is optional but tool will fail without it
class BadDatabaseTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[],
        optional_permissions=[Permission.DB_READ],  # Should be required!
    )
    
    def run(self, context: ToolContext) -> ToolResult:
        results = self.db.query("SELECT * FROM users")  # Will fail without DB_READ!
        ...
```

**Why it's wrong:**
- Misleading — tool will fail if permission denied
- Breaks authorization contract
- Confuses reviewers and users

**✅ Fix:** Use required_permissions for essential access

```python
# ✅ GOOD — DB_READ is required
class GoodDatabaseTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[Permission.DB_READ],  # Essential for tool
        optional_permissions=[],
    )
    
    def run(self, context: ToolContext) -> ToolResult:
        results = self.db.query("SELECT * FROM users")
        ...
```

---

### ❌ Anti-Pattern 5: Mixing Personas

**Problem:** Tool designed for multiple personas with conflicting requirements

```python
# ❌ BAD — tool tries to serve both core and infra personas
class BadMultiPersonaTool(ToolBase):
    permissions = ToolPermissions(
        required_permissions=[
            Permission.NET_HTTP,   # Core persona can use
            Permission.EXEC_SHELL, # Only infra persona allowed
        ],
    )
```

**Why it's wrong:**
- Tool cannot be used by core persona (needs EXEC_SHELL)
- Unclear which persona should use this tool
- Violates single responsibility principle

**✅ Fix:** Split into focused tools per persona

```python
# ✅ GOOD — separate tools for different personas
class CoreAPITool(ToolBase):
    """For core persona agents."""
    permissions = ToolPermissions(
        required_permissions=[Permission.NET_HTTP],
    )

class InfraDeployTool(ToolBase):
    """For infra persona agents."""
    permissions = ToolPermissions(
        required_permissions=[Permission.EXEC_SHELL, Permission.NET_HTTP],
    )
```

---

## 6. Design Notes (Future Intent)

This section describes **future implementation plans** that are **NOT implemented in this PR**.

### Future: Tool Registry Reads Permissions

When PR-024 (Tool Registry v2) is implemented, the registry will:

1. **Read** the `permissions` property/attribute from each tool
2. **Store** permission metadata alongside tool metadata
3. **Expose** permission information to agents and runtime
4. **Enable** permission-based tool filtering

**Example (future):**
```python
# Future: Registry exposes tool permissions
registry = ToolRegistry()
tool = registry.get_tool("http_fetch")
print(tool.permissions.required_permissions)  # [Permission.NET_HTTP]
```

---

### Future: Runtime Authorization Hook

When PR-030 (Execution Pipeline) is implemented, the runtime will:

1. **Check** tool's required permissions against agent's allowed permissions
2. **Call** `authorize(tool, policy)` before `tool.run()`
3. **Block** execution if permissions denied
4. **Return** structured error explaining denial reason

**Example (future):**
```python
# Future: Runtime enforces permissions
def execute_tool(tool: ToolBase, context: ToolContext, policy: AgentPolicy):
    decision = authorize(tool, policy)
    
    if not decision.allowed:
        return ToolResult(
            ok=False,
            error=ToolError(
                code="PERMISSION_DENIED",
                message=decision.reason,
                retryable=False,
            ),
            ...
        )
    
    return tool.run(context)  # Execute if authorized
```

---

### Clearly Stated: This PR Does NOT Implement These

⚠️ **Important Disclaimers:**

1. **No enforcement** — permissions are not checked at runtime
2. **No registry integration** — Tool Registry does not read permissions yet
3. **No authorization hook** — `authorize()` function does not exist yet
4. **No CI validation** — no CI checks enforce permission declarations
5. **Fully optional** — tools can run without declaring permissions

**Purpose of this PR:**
- Establish conventions and examples
- Create shared vocabulary for permissions
- Prepare for future enforcement (PR-024, PR-030)
- Improve code review clarity starting now

---

## Summary

This document provides **practical guidance** for declaring permissions in Tools:

1. **Reference the mapping table** when designing new tools (Section 2)
2. **Study the examples** to understand permission patterns (Section 3)
3. **Declare permissions explicitly** using `ToolPermissions` (Section 4)
4. **Avoid anti-patterns** that lead to unclear or unsafe tools (Section 5)
5. **Understand this is design-only** — no enforcement yet (Section 6)

### Key Takeaways

- ✅ **Always declare permissions** — even if not enforced yet
- ✅ **Use least privilege** — request only what's needed
- ✅ **Be explicit** — make intent clear for reviewers
- ✅ **Follow examples** — consistent patterns across tools
- ✅ **Think ahead** — future PRs will integrate these declarations

### Next Steps

After this PR merges:

1. **PR-024:** Tool Registry v2 reads and stores permission metadata
2. **PR-030:** Execution Pipeline enforces permissions via `authorize()` hook
3. **Future:** Path restrictions, audit logging, dynamic policy updates

### Questions?

If you have questions about permission declarations:

1. Review the examples in this document
2. Check `docs/TOOL_PERMISSIONS.md` for design rationale
3. Look at `DummyTool` implementation for reference
4. Ask in team chat or GitHub discussions
5. Propose updates to this doc via PR

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-23  
**Related Docs:**
- `docs/TOOL_PERMISSIONS.md` — Permission model design
- `docs/TOOLS.md` — Tool authoring guide
- `packages/core/tools/permissions.py` — Permission types and schemas
