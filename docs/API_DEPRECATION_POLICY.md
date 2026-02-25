# PR-050: API Deprecation Policy

## Purpose

This document establishes the deprecation policy for FlowBiz AI Core API endpoints. It ensures consumers have adequate notice and migration paths when breaking changes are introduced.

## Versioning Strategy

- **Major versions** (v1, v2, v3): Breaking changes → new version prefix
- **Minor versions**: Additive changes (new fields, endpoints) → same prefix
- **Patch versions**: Bug fixes, no schema changes

## Deprecation Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| **Announcement** | Day 0 | Add `Deprecation` header to affected endpoints; update docs |
| **Sunset Warning** | 30 days | Add `Sunset` header with removal date |
| **Migration Period** | 60 days | Both old and new endpoints available simultaneously |
| **Removal** | 90 days | Old endpoint returns `410 Gone` |
| **Cleanup** | 120 days | Remove old endpoint code completely |

## Deprecation Headers

Deprecated endpoints should include standard deprecation headers:

```
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Link: </v2/meta>; rel="successor-version"
```

## Migration Guide Template

When deprecating an endpoint, create a migration guide:

```
## Migrating from /v1/endpoint to /v2/endpoint

### What changed
- Field `x` renamed to `y`
- Response format changed from flat to nested

### How to migrate
1. Update client to use `/v2/endpoint`
2. Map field `x` → `y` in response parsing
3. Update SDK version to >= 2.0.0

### Timeline
- Old endpoint available until: 2027-01-01
- New endpoint available from: 2026-10-01
```

## Current API Versions

| Version | Status | Notes |
|---------|--------|-------|
| v1 | **Active** | Primary API version |
| v2 | **Active** | Extended metadata, capabilities |

## Responsibilities

- **Core team**: Announce deprecations, provide migration guides, implement sunset headers
- **SDK team**: Update generated clients within 7 days of new version launch
- **Consumers**: Migrate within the 90-day migration period
