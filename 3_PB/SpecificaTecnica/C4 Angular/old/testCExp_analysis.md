# UC-3 Search – Class Diagram Analysis (`testCExp.puml`)

> Strict review against SOLID principles, Smart/Dumb pattern, C3 consistency, Angular 17+ best practices.

---

## Critical Violations

### 1 — DIP broken: `SearchPageComponent` injects concrete classes
`searchFacade: SearchFacade` and `semanticFacade: SemanticIndexFacade` are injected as concrete types.  
No `ISearchFacade` interface exists. `semanticFacade` should be typed as the already-defined `ISemanticIndexStatus`.  
**Fix:** define `ISearchFacade`, inject all services through their interfaces.

---

### 2 — ISP broken: `SemanticIndexFacade` uses `ISearchChannel` for unrelated IPC calls
`SemanticIndexFacade` holds `ipcGateway: ISearchChannel`, but calls `getIndexingStatus` and `semantic:cancel` — methods that do not exist in `ISearchChannel`.  
**Fix:** extract a dedicated `ISemanticChannel` (or `IIndexingChannel`) interface.

---

### 3 — Smart component nested inside a Dumb component
`AdvancedFilterPanelComponent` (Dumb) instantiates `SubjectFilterComponent` (Smart) in its template.  
A Dumb component's template must never own a Smart child.  
**Fix:** either hoist `SubjectFilterComponent` rendering to `SearchPageComponent`, or flatten its wizard state to make it truly Dumb.

---

### 4 — `DocumentViewerComponent` classified differently vs. C3
Here it is Dumb with only `@Input documentId`.  
In `C3_Final_complete.puml` it injects `DocumentFacade` and triggers `ErrorDialog` — making it Smart.  
**Fix:** align classification; move it to the Smart package and add the facade injection.

---

## High-Severity Issues

### 5 — Dual validation error state (SRP / DRY)
`SearchState.validationErrors: Map<string, ValidationError>` duplicates `ValidationResult.errors`.  
`SearchFacade` must synchronise both, creating two update paths.  
**Fix:** embed a single `ValidationResult` field in `SearchState`; remove the naked map.

---

### 6 — Missing `@Output` return arrows for `DiDaiFilters` and `AggregateFilters`
`FilterValueInputComponent` has a return `@Output valueChanged` arrow only to `CommonFiltersComponent`.  
`DiDaiFiltersComponent` and `AggregateFiltersComponent` have no return arrows — ~60 % of filter-input flows are absent.  
**Fix:** add symmetrical `@Output` arrows for both parent components.

---

### 7 — Retry flow entirely unmodelled
`InlineErrorComponent` shows `'Riprova' if error.recoverable === true` but declares zero `@Output` events.  
There is no `@Output retryClicked`, no bubble-up arrow, and no `SearchFacade` handler for retry.  
**Fix:** add `@Output retryClicked: EventEmitter<void>` and trace the event back to `SearchPageComponent` → `SearchFacade.executeSearch()`.

---

### 8 — `ISemanticIndexStatus` interface too narrow
Interface exposes only `getStatus(): Signal<SemanticIndexState>`.  
`SemanticIndexFacade` also exposes `startIndexing()` and `cancelIndexing()`, which have no interface counterpart.  
**Fix:** either add those methods to the interface or split into `ISemanticIndexStatus` (read) + `ISemanticIndexControl` (write), following ISP.

---

### 9 — `AbortController` lifecycle unmodelled
`SearchFacade` holds `abortController: AbortController | null` and `cancelSearch()` exists, but:
- no arrow from `cancelSearch()` → `abortController.abort()`
- no flow showing cleanup after normal completion
- no guard for calling `abort()` when no search is in flight

**Fix:** model the lifecycle explicitly (create on `executeSearch`, abort on `cancelSearch`, nullify in `resetSearching`).

---

## Medium Issues

### 10 — `SEARCH_LATENCY_MS` in the wrong enum
`TelemetryEvent` enum includes `SEARCH_LATENCY_MS`, which is a string key for `trackTiming(name: string, ms: number)` — not a `TelemetryEvent`.  
Mixing the two breaks type safety against `ITelemetry`'s own signature.  
**Fix:** remove `SEARCH_LATENCY_MS` from `TelemetryEvent`; use a plain `string` constant or a separate `TelemetryMetric` enum.

---

### 11 — Missing UML multiplicities
`SearchState o-- SearchResult` should be `1 --> *` (the field is `SearchResult[]`).  
`ValidationResult o-- ValidationError` should also be `1 --> *` (the field is `Map<string, ValidationError>`).  
**Fix:** add multiplicities on both aggregation ends.

---

### 12 — `MetadataPanelComponent @Input` wrong type
Declared as `@Input documentId: string`.  
The C3 shows it receiving `@Input data: DocumentDetail` — a fully-resolved DTO.  
A raw `id` forces the Dumb component to fetch data itself, violating Dumb rules.  
**Fix:** change to `@Input documentDetail: DocumentDetail`.

---

## Low Issues

### 13 — `SubjectFilterComponent` mislabelled as Smart
The diagram's own legend defines Smart as "injects services via DI".  
The note on `SubjectFilterComponent` explicitly states "Does NOT inject services."  
It manages local `WritableSignal` state but has no service injection — it is a **stateful Dumb** component at most.  
**Fix:** move it to the Dumb package or introduce a "Stateful Dumb" stereotype; update the note to match.

---

### 14 — `IRouteGuard` models deprecated class-based guard
```
interface IRouteGuard {
  canActivate(route: ActivatedRouteSnapshot): boolean | UrlTree
}
```
Angular 15+ (and this project's Angular 17+ target) uses `CanActivateFn` (a plain function).  
The C3 already marks `DipReadyGuard` as `CanActivateFn`.  
**Fix:** remove `IRouteGuard`; express the guard as a typed functional guard (`CanActivateFn`).

---

## Summary Table

| # | Issue | Principle | Severity |
|---|---|---|---|
| 1 | `SearchPageComponent` injects concrete facades | DIP | Critical |
| 2 | `SemanticIndexFacade` uses `ISearchChannel` for unrelated calls | ISP | Critical |
| 3 | Smart child inside Dumb parent (`SubjectFilter` in `AdvancedFilterPanel`) | Smart/Dumb | Critical |
| 4 | `DocumentViewerComponent` is Dumb here, Smart in C3 | Consistency | Critical |
| 5 | Dual validation error state in `SearchState` + `ValidationResult` | SRP / DRY | High |
| 6 | `@Output` return arrows missing for `DiDai` and `Aggregate` filters | Flow | High |
| 7 | Retry flow (`InlineError @Output`) completely absent | Flow | High |
| 8 | `ISemanticIndexStatus` doesn't cover `startIndexing` / `cancelIndexing` | ISP | High |
| 9 | `AbortController` lifecycle unmodelled | Flow | High |
| 10 | `SEARCH_LATENCY_MS` placed in `TelemetryEvent` enum | Typing | Medium |
| 11 | Missing multiplicity on `SearchState o-- SearchResult` and `ValidationResult o-- ValidationError` | UML | Medium |
| 12 | `MetadataPanelComponent` receives `documentId` instead of `DocumentDetail` | Consistency | Medium |
| 13 | `SubjectFilterComponent` labelled Smart but injects no services | Naming | Low |
| 14 | `IRouteGuard` models deprecated class-based guard (Angular 17+ uses `CanActivateFn`) | Angular 17 | Low |
