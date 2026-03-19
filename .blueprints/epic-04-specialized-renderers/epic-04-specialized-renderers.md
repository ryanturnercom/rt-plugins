# Epic: Specialized Renderers

**Status:** [✓] Completed

## Context

The core HTML rendering engine (Epic 03) handles standard markdown sections. This epic adds specialized rendering for two content types that need custom treatment: OpenAPI specs (collapsible endpoint cards) and blueprint folders (appendix-style epic/task tables).

Dependencies: Epic 03 (core rendering engine must exist)

## Implementation Overview

Add two renderer modules to `generate_docs.py` that produce HTML fragments for their respective content types. These are called by the section assembler when a section has `type = "openapi"` or `type = "blueprints"`.

## Tasks

- [x] [task-01: OpenAPI renderer with collapsible endpoints](tasks/task-01-openapi-renderer.md)
- [✓] [task-02: Blueprint appendix renderer](tasks/task-02-blueprint-renderer.md)
- [✓] [task-03: Integrate renderers into section assembler](tasks/task-03-integrate-renderers.md)
