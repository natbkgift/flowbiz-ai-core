# Seed Templates (PR-103)

## Purpose

Provide **manifest contracts + example stubs** for reusable seed templates without implementing a template generator runtime in core.

## Scope in Core

PR-103 adds:
- `SeedTemplateManifest`, `SeedTemplateVariable`, `SeedTemplateFile`
- helper `required_template_variables()`
- example manifest stubs under `docs/contracts/stubs/seed_templates/`

## Out of Scope

- actual scaffold generator CLI/runtime
- platform/client-specific project bootstrapping logic
- IDE integration or UI template browsers

## Example Stubs

See:
- `docs/contracts/stubs/seed_templates/agent-basic.json`
- `docs/contracts/stubs/seed_templates/workflow-basic.json`

These files are examples for downstream generators to consume.
