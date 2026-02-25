# Slack Connector Spec (PR-111)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

Actual Slack integration implementation (webhook handling, signing verification, API calls, retries, secrets) is **out of scope** for core and belongs in platform/client repos.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `SlackConnectorConfig`
- `SlackEventEnvelope`
- `SlackMessageRequest`
- `SlackConnectorStub`

## Example Stub

- `docs/contracts/stubs/integrations/slack_event.json`

## Ownership Boundary

- Core: schema/contracts + deterministic stubs
- Platform/client: webhook endpoints, Slack SDK usage, secrets, retries, deployment
