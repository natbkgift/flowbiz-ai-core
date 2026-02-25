# Email Agent Spec (PR-114)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

Provider integrations (SMTP/SES/SendGrid/etc.), credentials, retries, and delivery pipelines are out of scope for core.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `EmailAgentConfig`
- `EmailSendRequest`
- `EmailSendResult`
- `EmailAgentStub`

## Example Stub

- `docs/contracts/stubs/integrations/email_send_request.json`

## Ownership Boundary

- Core: contracts/stubs/tests/docs
- Platform/client: provider adapters, credentials, queues/retries, deliverability handling
