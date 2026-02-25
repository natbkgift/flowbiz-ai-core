# WhatsApp Connector Spec (PR-113)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

Actual WhatsApp provider integration (webhooks, verification, messaging APIs, retries) must be implemented in platform/client code.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `WhatsAppConnectorConfig`
- `WhatsAppWebhookEvent`
- `WhatsAppSendMessageRequest`
- `WhatsAppConnectorStub`

## Example Stub

- `docs/contracts/stubs/integrations/whatsapp_event.json`

## Ownership Boundary

- Core: contracts/stubs/tests/docs
- Platform/client: provider SDK/API usage, secrets, delivery logic, deploy/runtime
