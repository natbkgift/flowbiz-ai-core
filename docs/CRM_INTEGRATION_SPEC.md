# CRM Integration Spec (PR-115)

## Status

Contracts/stubs/docs only in `flowbiz-ai-core`.

Provider-specific CRM integrations (HubSpot/Salesforce/etc.), credentials, sync scheduling, and retries are out of scope for core.

## Added Contracts

In `packages/core/contracts/integrations.py`:
- `CRMIntegrationConfig`
- `CRMSyncRequest`
- `CRMSyncResult`
- `CRMIntegrationStub`

## Example Stub

- `docs/contracts/stubs/integrations/crm_sync_request.json`

## Ownership Boundary

- Core: contracts/stubs/tests/docs
- Platform/client: CRM provider adapters, sync jobs, secret management, error handling
