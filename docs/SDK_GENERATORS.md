# SDK Generators (PR-108)

## Purpose

Define **SDK generator specification contracts** and example stubs for downstream tooling without implementing generator runtimes inside `flowbiz-ai-core`.

## Added Contracts

In `packages/core/contracts/devx.py` (PR-108 section):
- `SDKGeneratorTarget`
- `SDKGeneratorSpec`
- `sdk_target_languages(spec)`

## Scope Notes

- Core stores contracts/examples only
- Language-specific generators (Python/TypeScript/etc.) belong in tooling/platform repos
- Publishing to package registries is out of scope for core

## Example Stubs

- `docs/contracts/stubs/sdk_generators/openapi-python-ts.json`
