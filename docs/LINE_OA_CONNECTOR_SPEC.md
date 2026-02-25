# LINE OA Connector Spec (PR-112)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

Actual LINE OA webhook handling, signature verification, and messaging API integration must be implemented outside core.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `LineOAConnectorConfig`
- `LineOAWebhookEvent`
- `LineOAReplyRequest`
- `LineOAConnectorStub`

## Example Stub

- `docs/contracts/stubs/integrations/line_oa_event.json`

## Ownership Boundary

- Core: contracts/stubs/tests/docs
- Platform/client: LINE SDK integration, credentials, webhooks, retries, deployment
