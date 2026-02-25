# Example Agents (PR-104)

## Purpose

Provide **deterministic reference agents** in core for developer onboarding, tests, and contract examples.

## Included Examples

- `TemplateReplyAgent` — stable formatted reply from `input_text`
- `MetadataEchoAgent` — echoes sorted metadata keys for deterministic tracing examples

Location: `packages/core/agents/examples.py`

## Scope Notes

- These are **reference implementations** only.
- No platform-specific integrations or external API calls.
- No secrets, network I/O, or non-deterministic behavior.

## Example Usage

```python
from packages.core.agents.context import AgentContext
from packages.core.agents.examples import TemplateReplyAgent

agent = TemplateReplyAgent()
ctx = AgentContext.create(input_text="hello")
result = agent.run(ctx)
assert result.output_text == "[template-reply] hello"
```
