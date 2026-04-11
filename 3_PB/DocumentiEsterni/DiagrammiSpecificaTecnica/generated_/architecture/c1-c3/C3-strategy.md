# C3 Strategy: Readability + Completeness

Best choice for this codebase is **multiple focused C3 diagrams** instead of one monolithic C3.

Why:
- A single C3 quickly becomes crowded because Main process includes multiple IPC adapters, many use cases, repositories, DAOs, and external integrations.
- Focused views keep each diagram readable while still exposing complete architecture across the full set.

Adopted split:
- `C3-main-search-flow.puml`: search text, advanced, semantic, and metadata-keys path.
- `C3-main-indexing-flow.puml`: DIP indexing pipeline and vector generation.
- `C3-main-integrity-browsing-fileops.puml`: browse/integrity checks and export/print operations.

Frontend split:
- `C3-renderer-search-indexing-flow.puml`: SearchPage, SearchFacade, Search/Indexing IPC gateways, shared services.
- `C3-renderer-navigation-detail-integrity-export.puml`: AppShell/navigation tree, item detail fallback, integrity dashboard, export page and related gateways.

SOLID and patterns are highlighted in each diagram note.
