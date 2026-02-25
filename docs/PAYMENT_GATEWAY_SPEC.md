# Payment Gateway Spec (PR-116)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

**Important:** Billing/payment processing is out of scope for core per `docs/SCOPE.md`. This PR provides only boundary contracts/stubs for downstream platform adapters.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `PaymentGatewayConfig`
- `PaymentEventEnvelope`
- `PaymentVerificationRequest`
- `PaymentGatewayStub`

## Example Stub

- `docs/contracts/stubs/integrations/payment_event.json`

## Ownership Boundary

- Core: contracts/stubs/tests/docs only
- Platform/billing service: provider SDKs, payment processing, webhooks, reconciliation, compliance, secrets
