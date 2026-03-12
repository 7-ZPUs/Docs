# UC-3 Search – Class Diagram Analysis Report

**Files analysed:** `testCExp.puml` (v3) → `Correction.puml` (v4) → `Correction.puml` (v5)  
**Reference diagrams:** `UC3_Search.puml`, `C3_Final_complete.puml`  
**Standard:** SOLID · Smart/Dumb · Angular 17+ · UML class diagram notation  
**Rounds:** 3  
**Date:** 2026-03-10  

---

## Round 1 — `testCExp.puml` (v3)

### Critical

#### C1 — DIP: `SearchPageComponent` injects concrete classes
```
- searchFacade:   SearchFacade        <<inject>>   ← concrete
- semanticFacade: SemanticIndexFacade <<inject>>   ← concrete
```
No `ISearchFacade` exists. `semanticFacade` should be typed as the already-defined `ISemanticIndexStatus`.  
Both injections depend on implementations, breaking DIP entirely.  
**Fix:** define `ISearchFacade`; type all injections through interfaces.

---

#### C2 — ISP: `SemanticIndexFacade` uses `ISearchChannel` for unrelated IPC calls
`SemanticIndexFacade.ipcGateway: ISearchChannel` but calls `getIndexingStatus` and `semantic:cancel` — neither method exists in `ISearchChannel`.  
**Fix:** extract a dedicated `IIndexingChannel` (or `ISemanticChannel`) interface.

---

#### C3 — Smart/Dumb: Smart child inside a Dumb parent
`AdvancedFilterPanelComponent` (Dumb) instantiates `SubjectFilterComponent` (Smart) in its template.  
A Dumb component must never own a Smart child.  
**Fix:** demote `SubjectFilterComponent` to Dumb/StatefulDumb, or hoist it to `SearchPageComponent`.

---

#### C4 — C3 inconsistency: `DocumentViewerComponent` classified as Dumb
The class diagram places it in the Dumb package with only `@Input documentId`.  
`C3_Final_complete.puml` shows it injecting `DocumentFacade` and triggering `ErrorDialog` — making it Smart.  
**Fix:** move to the Smart package; add facade injection and error delegation.

---

### High

#### H1 — SRP/DRY: dual validation error state
`SearchState.validationErrors: Map<string, ValidationError>` duplicates `ValidationResult.errors`.  
Two update paths exist for the same data, violating SRP on `SearchFacade`.  
**Fix:** drop `validationErrors` from `SearchState`; embed a single `ValidationResult` field.

---

#### H2 — Missing `@Output` return arrows for `DiDaiFilters` and `AggregateFilters`
`FilterValueInputComponent` return arrows exist only for `CommonFiltersComponent`.  
~60 % of filter-input output flows are absent.  
**Fix:** add symmetric `@Output valueChanged / validationError` arrows for all three parent components.

---

#### H3 — Retry flow entirely absent
`InlineErrorComponent` states `'Riprova' if error.recoverable` but declares zero `@Output` events.  
No event, no bubble-up arrow, no handler in `SearchFacade`.  
**Fix:** add `@Output retryClicked: EventEmitter<void>`; trace the event chain to `SearchPageComponent` and the facade.

---

#### H4 — ISP: `ISemanticIndexStatus` too narrow
Interface exposes only `getStatus()`. `SemanticIndexFacade` also exposes `startIndexing()` and `cancelIndexing()` — no interface counterpart.  
**Fix:** split into `ISemanticIndexStatus` (read) and `ISemanticIndexControl` (write).

---

#### H5 — `AbortController` lifecycle unmodelled
`SearchFacade` holds `abortController: AbortController | null` and `cancelSearch()` exists, but the create / abort / nullify lifecycle is never expressed.  
**Fix:** add `createAbortController()` and `abortAndReset()` private helpers; document cleanup in `resetSearching()`.

---

### Medium

#### M1 — `TelemetryEvent` enum contains a timing key
`SEARCH_LATENCY_MS` belongs to `trackTiming(name: string, ms: number)`, not to `trackEvent(name: TelemetryEvent)`.  
Placing it in `TelemetryEvent` breaks type safety against `ITelemetry`'s own signature.  
**Fix:** remove from the enum; use a separate `TelemetryMetric` enum or a `string` constant.

#### M2 — Missing UML multiplicities
`SearchState o-- SearchResult` (`1 → *`) and `ValidationResult o-- ValidationError` (`1 → *`) lack cardinalities.  
**Fix:** add explicit multiplicities on both ends.

#### M3 — `MetadataPanelComponent @Input` wrong type
Declared as `@Input documentId: string`.  
C3 shows it receiving `@Input documentDetail: DocumentDetail` — a fully-resolved DTO.  
A bare `id` forces the Dumb component to fetch, violating Dumb rules.  
**Fix:** change to `@Input detail: DocumentDetail`.

---

### Low

#### L1 — `SubjectFilterComponent` mislabelled as Smart
The legend defines Smart as "injects services via DI". The component's own note says "Does NOT inject services."  
It manages local `WritableSignal` state only. Calling it Smart pollutes the visual language.  
**Fix:** relabel as `<<StatefulDumb>>`.

#### L2 — `IRouteGuard` models deprecated class-based guard
Angular 15+ (and this project's 17+ target) uses `CanActivateFn`. The interface is never consumed by Angular's DI system.  
**Fix:** remove `IRouteGuard`; represent the guard as a typed functional `CanActivateFn`.

---

### Round 1 — Summary

| # | Issue | Principle | Severity |
|---|---|---|---|
| C1 | `SearchPageComponent` injects concrete `SearchFacade` / `SemanticIndexFacade` | DIP | Critical |
| C2 | `SemanticIndexFacade` uses `ISearchChannel` for unrelated IPC calls | ISP | Critical |
| C3 | Smart child (`SubjectFilterComponent`) inside Dumb parent | Smart/Dumb | Critical |
| C4 | `DocumentViewerComponent` is Dumb here, Smart in C3 | Consistency | Critical |
| H1 | Dual validation error state in `SearchState` + `ValidationResult` | SRP / DRY | High |
| H2 | `@Output` return arrows missing for `DiDai` and `Aggregate` filters | Data flow | High |
| H3 | Retry flow (`InlineErrorComponent @Output`) completely absent | Data flow | High |
| H4 | `ISemanticIndexStatus` does not cover `startIndexing` / `cancelIndexing` | ISP | High |
| H5 | `AbortController` lifecycle unmodelled | Data flow | High |
| M1 | `SEARCH_LATENCY_MS` in `TelemetryEvent` enum | Typing | Medium |
| M2 | Missing multiplicity on collection aggregations | UML | Medium |
| M3 | `MetadataPanelComponent @Input` is `id` instead of `DocumentDetail` | Consistency | Medium |
| L1 | `SubjectFilterComponent` labelled Smart but injects no services | Naming | Low |
| L2 | `IRouteGuard` models deprecated class-based guard (Angular 17+) | Angular 17 | Low |

---

---

## Round 2 — `Correction.puml` (v4)

All 14 issues from Round 1 were addressed. The following problems remain or were newly introduced.

### Critical

#### C1 — `SearchPageComponent` injects `ISemanticIndexControl` without C3 justification
```
- semanticControl: ISemanticIndexControl <<inject>>
```
Neither `UC3_Search.puml` nor `C3_Final_complete.puml` places indexing control in the search page. The C3 shows only read access (`legge Signal<SemanticIndexState>.status`). Adding write control here violates SRP — search and indexing control are distinct responsibilities belonging to different pages.  
**Fix:** remove `ISemanticIndexControl` from `SearchPageComponent`. Indexing control belongs to the DIP loading flow.

---

#### C2 — `onRetrySearch()` calls a method not on `ISearchFacade`
The `InlineErrorComponent` note states:
> "bubbles → SearchPageComponent → `ISearchFacade.cancelSearch()` + `executeSearch()`"

`executeSearch()` is declared **private** inside `SearchFacade` and is absent from `ISearchFacade`. A Smart component programming to the interface cannot invoke it.  
**Fix:** add `retry(): void` to `ISearchFacade` (or map retry to `setQuery()` with the current state); remove the private method reference from design documentation.

---

#### C3 — `DocumentViewerComponent` missing required `@Input`s; `@Output viewerError` unconnected
C3 mandates `@Input documentId, mimeType, fileName`. v4 declares only `@Input documentId`.  
`@Output viewerError: EventEmitter<AppError>` is declared but has no return arrow to `SearchPageComponent` in the data-flow section — the event is emitted into a void.  
**Fix:** add `mimeType: string` and `fileName: string` inputs; add a `viewerError` return arrow to `SearchPageComponent.onViewerError()`.

---

#### C4 — `DipReadyGuard` still breaks DIP and misrepresents `CanActivateFn`
```plantuml
class DipReadyGuard <<CanActivateFn>> {
    - dipFacade: DipFacade   ← concrete, DIP broken
    + execute(...)           ← functional guards have no named method
}
```
Two sub-issues:
- Injects concrete `DipFacade`; should depend on an abstraction (e.g. `IDipReadyChecker`).
- A `CanActivateFn` is a plain function — no class, no `execute()` method. The fix is cosmetic only.  

**Fix:** remove the class model; represent it as a note or a type alias `DipReadyGuard: CanActivateFn`. Introduce `IDipReadyChecker` if the guard logic needs to be testable in isolation.

---

### High

#### H1 — `IIndexingChannel.startIndexing()` and `cancelIndexing()` return `void`
Both are async IPC calls over Electron's context bridge. Returning `void` gives the caller no error path and no confirmation of completion. `IErrorHandler` can never be invoked on their failures.  
**Fix:** change return types to `Observable<void>` (consistent with the rest of the channel interface).

---

#### H2 — Dual validation path still present
`AdvancedFilterPanelComponent` emits `@Output validationResult: EventEmitter<ValidationResult>`  
AND `SearchFacade` writes `SearchState.validationResult` via `FilterValidatorService.validate()`.

Two separate paths produce `ValidationResult` objects. It is unspecified which is authoritative and whether they can diverge.  
**Fix:** pick one path. Recommended: `SearchFacade` is the single authority; `AdvancedFilterPanelComponent @Output validationResult` is removed and the panel reads errors via the `@Input filters`-driven validation only.

---

#### H3 — `MetadataPanelComponent` is an orphan in this diagram
Present in the Dumb package with no data-flow arrows. It belongs to the Document Detail module, not to UC-3 Search.  
**Fix:** remove it from this diagram; it should appear in the Document Detail class diagram only.

---

### Medium

#### M1 — Fix #11 (multiplicities) is incomplete
Five aggregation relations still carry no cardinalities:

| Relation | Required cardinality |
|---|---|
| `SearchState o-- SearchQuery` | `1 -- 1` |
| `SearchState o-- SearchFilters` | `1 -- 1` |
| `SearchState o-- ValidationResult` | `1 -- 1` |
| `SearchFilters o-- SubjectCriteria` | `"1" o-- "0..1"` |
| `SemanticIndexState *-- IndexingStatus` | `1 *-- 1` |

---

#### M2 — `FilterValueInputComponent` return arrows incorrectly model a single `EventEmitter` as three
```plantuml
FilterValueInputComponent --> CommonFiltersComponent   : "▲ @Output …"
FilterValueInputComponent --> DiDaiFiltersComponent    : "▲ @Output …"
FilterValueInputComponent --> AggregateFiltersComponent: "▲ @Output …"
```
A component has one `@Output` per event; the same emitter fires to whichever parent binds to it via template. Three separate arrows imply three distinct outputs, misleading implementors.  
**Fix:** show a single `@Output valueChanged` and `@Output validationError` on the class; replace the three arrows with a single note clarifying "host parent receives via template binding".

---

#### M3 — `abortController` exposed as a visible class field
```plantuml
- abortController: AbortController | null
```
The private lifecycle helpers `createAbortController()` and `abortAndReset()` already encapsulate it. Listing the raw field on the class surface leaks implementation detail that should be invisible to consumers.  
**Fix:** remove the field from the visible member list; keep it as a comment inside the `..` note section.

---

### Round 2 — Summary

| # | Issue | Principle | Severity |
|---|---|---|---|
| C1 | `SearchPageComponent` injects `ISemanticIndexControl` (not in UC-3 C3) | SRP | Critical |
| C2 | `onRetrySearch()` calls private `executeSearch()` — not on `ISearchFacade` | DIP / Encapsulation | Critical |
| C3 | `DocumentViewerComponent` missing `mimeType`/`fileName`; `viewerError` unconnected | C3 / Data flow | Critical |
| C4 | `DipReadyGuard` injects concrete `DipFacade`; `execute()` misrepresents `CanActivateFn` | DIP / Angular 17 | Critical |
| H1 | `IIndexingChannel.startIndexing()` / `cancelIndexing()` return `void` (no async error path) | Error handling | High |
| H2 | Dual `ValidationResult` path: `SearchFacade` + panel `@Output` both produce it | SRP / DRY | High |
| H3 | `MetadataPanelComponent` is an orphan — wrong UC context, no data-flow arrows | Diagram quality | High |
| M1 | Fix #11 incomplete — 5 aggregation relations still lack multiplicities | UML | Medium |
| M2 | Three `@Output` return arrows on `FilterValueInputComponent` — wrong UML for a single `EventEmitter` | UML | Medium |
| M3 | `abortController` field exposed as visible member — should be hidden behind private helpers | Encapsulation | Medium |

---

---

## Round 3 — `Correction.puml` (v5)

All 10 issues from Round 2 were addressed. The following problems remain or were newly introduced.

### Critical

#### C1 — DIP: `DocumentViewerComponent` injects concrete `DocumentFacade`

```plantuml
- documentFacade: DocumentFacade  <<inject>>
```

Every other Smart component in v5 injects only interface types. `DocumentFacade` is a concrete class and no `IDocumentFacade` abstraction is declared (nor referenced). The DIP goal stated for the entire diagram is violated by the only remaining concrete injection.

**Fix:** declare `IDocumentFacade` (or reference it from the Document Detail module) and type the injection as `IDocumentFacade`.

---

#### C2 — `IDipReadyChecker` declared in the Search UC diagram but its only implementor belongs to another module

```plantuml
package "Interfaces & Contracts" {
  interface IDipReadyChecker <<ISP>> { + isReady(): boolean }
}
' DipFacade ..|> IDipReadyChecker  — defined in DIP loading module
```

Declaring the interface inside the Search diagram forces the DIP Loading module to depend on a type defined in the Search module — a reverse cross-module dependency. Bounded contexts must own their own contracts.

**Fix:** move `IDipReadyChecker` to a shared kernel / cross-cutting contracts package; reference it in both modules rather than declaring it in one and implementing it in the other.

---

### High

#### H1 — `ISemanticIndexControl` is implemented but never consumed in this UC

After removing it from `SearchPageComponent` (R2-C1 fix):
- `SemanticIndexFacade ..|> ISemanticIndexControl` — implementation exists
- Zero `<<inject>>` or `<<uses>>` arrows point to `ISemanticIndexControl` in the data-flow section

An interface that is implemented but never consumed within its own diagram is dead weight. It implies a responsibility that does not belong to the Search UC.

**Fix:** remove `ISemanticIndexControl` entirely from this diagram. It belongs to the DIP Loading module's diagram.

---

#### H2 — Dual validation path reintroduced under a different form

`AdvancedFilterPanelComponent` receives both:
```plantuml
+ @Input  validator: FilterValidatorFn      ← called per-keystroke by the panel
+ @Input  validationResult: ValidationResult ← pushed from SearchState via facade
```

Two separate mechanisms produce validation errors for the same fields simultaneously, with no defined authority. The diagram does not specify which source feeds `FieldErrorComponent` under each sub-panel, nor what happens when they diverge. This is a SRP/DRY violation in a new form.

**Fix:** choose one authority. Either:
- The panel uses `validator` exclusively for real-time display and `validationResult @Input` is removed; or
- The facade is the sole authority, `validator @Input` is removed from the panel and the panel renders errors from `validationResult` only.

---

#### H3 — `FilterValueInputComponent` return arrow structurally contradicts its own note

```plantuml
FilterValueInputComponent -[#15803D]-> CommonFiltersComponent
  : "▲ @Output valueChanged / validationError [template-bound by host parent]"
```

The label states the output is template-bound to whichever parent instantiates the component, yet the arrow structurally targets `CommonFiltersComponent` exclusively. An arrow in a class diagram expresses a static structural relationship. Pointing to one specific class while the note says "any host" is contradictory and implies `FilterValueInputComponent` has knowledge of `CommonFiltersComponent` that a Dumb component must not have.

**Fix:** remove the return arrow entirely. The `@Output` declarations on the class box are sufficient. Replace with a class-level note: "host parent binds `valueChanged` / `validationError` in its own template."

---

### Medium

#### M1 — `ISearchFacade.retry()` contract is unspecified

```plantuml
+ retry(): void
```

No documentation states what `retry()` does: does it re-run the last full-text query, the last advanced search, or both? Does it require `isSearching === false` as a precondition? Does it implicitly call `cancelSearch()` first? An interface method with zero documented semantics cannot be correctly implemented or tested.

**Fix:** add a `.. retry re-executes last query/filters from current SearchState; calls abortAndReset() first if in flight ..` note below the interface.

---

#### M2 — `AppRouter` models a non-existent Angular API

```plantuml
class AppRouter {
    + navigate(path: string): void    ← wrong signature
    + lazyLoad(path: string): void    ← does not exist
}
```

Angular `Router.navigate()` accepts `commands: any[]` and optional `NavigationExtras`, not a bare `string`. `lazyLoad()` is not a method on `@angular/router` — lazy loading is a static route configuration, not a runtime call.

**Fix:** model the real `Router.navigate(commands: any[], extras?: NavigationExtras): Promise<boolean>` signature, or wrap it behind an `IRouter` abstraction exposing only the surface the diagram actually uses.

---

#### M3 — Private method `executeSearch()` still listed as a named class member

```plantuml
- executeSearch(q: SearchQuery, f: SearchFilters): void
```

Class diagrams express design contracts, not implementation details. Listing a private method gives it visibility it must not have and invites callers to reference it. The v5 note correctly documents it in prose — the member declaration should be removed.

**Fix:** delete the `- executeSearch(…)` line from `SearchFacade`'s member list; keep the behaviour description in the `..` note section only.

---

#### M4 — `ISemanticIndexControl` and `IIndexingChannel` expose identical method names across two abstraction layers

```plantuml
interface ISemanticIndexControl {
    + startIndexing(): Observable<void>   // identical
    + cancelIndexing(): Observable<void>  // identical
}
interface IIndexingChannel {
    + getIndexingStatus(): Observable<SemanticIndexState>
    + startIndexing(): Observable<void>   // identical
    + cancelIndexing(): Observable<void>  // identical
}
```

`ISemanticIndexControl` is the service boundary; `IIndexingChannel` is the IPC transport layer. Having verbatim duplicate method signatures collapses their semantic distinction. `SemanticIndexFacade` implements the former and uses the latter — both with the same names — making delegation indistinguishable by reading the diagram.

**Fix:** `IIndexingChannel` should expose transport-level primitives only (e.g. `sendStartIndexing(): Observable<void>`). `ISemanticIndexControl` expresses business intent. Different names reinforce the layer boundary.

---

### Round 3 — Summary

| # | Issue | Principle | Severity |
|---|---|---|---|
| C1 | `DocumentViewerComponent` injects concrete `DocumentFacade` | DIP | Critical |
| C2 | `IDipReadyChecker` declared in Search UC; implementor in a different module | Module boundaries | Critical |
| H1 | `ISemanticIndexControl` implemented but never consumed in this UC | ISP / Diagram quality | High |
| H2 | Dual validation path: `@Input validator` + `@Input validationResult` both active | SRP / DRY | High |
| H3 | `FilterValueInputComponent` return arrow targets only `CommonFiltersComponent` despite "template-bound" claim | UML / Smart-Dumb | High |
| M1 | `ISearchFacade.retry()` has no documented contract or preconditions | Interface design | Medium |
| M2 | `AppRouter.lazyLoad()` non-existent; `navigate(path: string)` wrong Angular signature | Angular accuracy | Medium |
| M3 | Private `executeSearch()` still listed as visible class member | Encapsulation | Medium |
| M4 | `startIndexing()` / `cancelIndexing()` duplicated across `ISemanticIndexControl` and `IIndexingChannel` | ISP / Layering | Medium |

---

---

## Cumulative Issue Register

> Status column reflects the state at the **end of each subsequent version**.  
> ✅ Fixed · ⚠ Partially fixed · ❌ Open

| ID | Introduced | Round | Issue | Principle | Severity | Status after v4 | Status after v5 |
|---|---|---|---|---|---|---|---|
| R1-C1 | v3 | 1 | Smart injects concrete `SearchFacade` / `SemanticIndexFacade` | DIP | Critical | ⚠ `ISearchFacade` added; `ISemanticIndexControl` overcorrection introduced | ✅ All injections via interfaces |
| R1-C2 | v3 | 1 | `SemanticIndexFacade` uses `ISearchChannel` for unrelated IPC calls | ISP | Critical | ✅ `IIndexingChannel` extracted | ✅ |
| R1-C3 | v3 | 1 | Smart child (`SubjectFilterComponent`) inside Dumb parent | Smart/Dumb | Critical | ✅ Demoted to `<<StatefulDumb>>` | ✅ |
| R1-C4 | v3 | 1 | `DocumentViewerComponent` Dumb here, Smart in C3 | C3 Consistency | Critical | ⚠ Moved to Smart; inputs/outputs incomplete | ⚠ Inputs added; DIP still broken (concrete `DocumentFacade`) |
| R1-H1 | v3 | 1 | Dual validation error state in `SearchState` + `ValidationResult` | SRP / DRY | High | ⚠ `validationErrors` map removed; `@Output validationResult` introduces new dual path | ⚠ Dual path persists as `@Input validator` + `@Input validationResult` |
| R1-H2 | v3 | 1 | `@Output` return arrows missing for DiDai + Aggregate filters | Data flow | High | ✅ Symmetric arrows added | ⚠ Arrow targets only `CommonFiltersComponent`; structural contradiction with note |
| R1-H3 | v3 | 1 | Retry flow entirely absent | Data flow | High | ⚠ Arrows added; `ISearchFacade.retry()` missing | ✅ `retry()` on interface; chain fully modelled |
| R1-H4 | v3 | 1 | `ISemanticIndexStatus` too narrow | ISP | High | ✅ Split to Status + Control | ✅ |
| R1-H5 | v3 | 1 | `AbortController` lifecycle unmodelled | Data flow | High | ⚠ Helpers declared; field still visible | ✅ Field hidden; lifecycle in note only |
| R1-M1 | v3 | 1 | `SEARCH_LATENCY_MS` in `TelemetryEvent` | Typing | Medium | ✅ `TelemetryMetric` enum extracted | ✅ |
| R1-M2 | v3 | 1 | Missing multiplicities on collection aggregations | UML | Medium | ⚠ 2 of 7 done | ✅ All 7 complete |
| R1-M3 | v3 | 1 | `MetadataPanelComponent @Input` wrong type | Consistency | Medium | ⚠ Type corrected; component still orphaned | ✅ Component removed (wrong UC) |
| R1-L1 | v3 | 1 | `SubjectFilterComponent` mislabelled Smart | Naming | Low | ✅ `<<StatefulDumb>>` | ✅ |
| R1-L2 | v3 | 1 | `IRouteGuard` class-based guard (Angular 17+) | Angular 17 | Low | ✅ Interface removed | ✅ |
| R2-C1 | v4 | 2 | `ISemanticIndexControl` injected in `SearchPageComponent` (no C3 basis) | SRP | Critical | N/A (introduced in v4) | ✅ Removed from `SearchPageComponent` |
| R2-C2 | v4 | 2 | `onRetrySearch()` calls private `executeSearch()` — not on interface | DIP / Encapsulation | Critical | N/A | ✅ `ISearchFacade.retry()` added; chain documented |
| R2-C3 | v4 | 2 | `DocumentViewerComponent` missing `mimeType`/`fileName`; `viewerError` unconnected | C3 / Data flow | Critical | N/A | ⚠ Inputs added; DIP violation (concrete `DocumentFacade`) remains |
| R2-C4 | v4 | 2 | `DipReadyGuard` injects concrete `DipFacade`; misrepresents `CanActivateFn` | DIP / Angular 17 | Critical | N/A | ⚠ `IDipReadyChecker` introduced; guard modelled as note; interface in wrong module |
| R2-H1 | v4 | 2 | `IIndexingChannel` methods return `void` (no async error path) | Error handling | High | N/A | ✅ Return types changed to `Observable<void>` |
| R2-H2 | v4 | 2 | Dual `ValidationResult` production path | SRP / DRY | High | N/A | ⚠ `@Output` removed; new dual path via `@Input validator` + `@Input validationResult` |
| R2-H3 | v4 | 2 | `MetadataPanelComponent` orphaned, wrong UC context | Diagram quality | High | N/A | ✅ Removed |
| R2-M1 | v4 | 2 | 5 aggregation relations still lacking multiplicities | UML | Medium | N/A | ✅ All complete |
| R2-M2 | v4 | 2 | Three `@Output` arrows for one `EventEmitter` | UML | Medium | N/A | ⚠ Note added; structural arrow still contradicts it |
| R2-M3 | v4 | 2 | `abortController` exposed as visible class field | Encapsulation | Medium | N/A | ✅ Hidden in note only |
| R3-C1 | v5 | 3 | `DocumentViewerComponent` injects concrete `DocumentFacade` | DIP | Critical | N/A | ❌ Open |
| R3-C2 | v5 | 3 | `IDipReadyChecker` declared in Search UC; implementor in different module | Module boundaries | Critical | N/A | ❌ Open |
| R3-H1 | v5 | 3 | `ISemanticIndexControl` implemented but never consumed in this UC | ISP / Diagram quality | High | N/A | ❌ Open |
| R3-H2 | v5 | 3 | Dual validation: `@Input validator` + `@Input validationResult` both active | SRP / DRY | High | N/A | ❌ Open |
| R3-H3 | v5 | 3 | `FilterValueInputComponent` return arrow targets `CommonFiltersComponent` only | UML / Smart-Dumb | High | N/A | ❌ Open |
| R3-M1 | v5 | 3 | `ISearchFacade.retry()` contract unspecified | Interface design | Medium | N/A | ❌ Open |
| R3-M2 | v5 | 3 | `AppRouter.lazyLoad()` non-existent; `navigate()` wrong signature | Angular accuracy | Medium | N/A | ❌ Open |
| R3-M3 | v5 | 3 | Private `executeSearch()` still listed as visible class member | Encapsulation | Medium | N/A | ❌ Open |
| R3-M4 | v5 | 3 | `startIndexing()` / `cancelIndexing()` duplicated across two interface layers | ISP / Layering | Medium | N/A | ❌ Open |

---

## Statistics

| Version | Total issues found | Critical | High | Medium | Low | Carried forward |
|---|---|---|---|---|---|---|
| v3 (Round 1) | 14 | 4 | 5 | 3 | 2 | — |
| v4 (Round 2) | 10 | 4 | 3 | 3 | 0 | 6 unresolved from v3 |
| v5 (Round 3) | 9 | 2 | 3 | 4 | 0 | 5 unresolved from v4 |
| **All-time total** | **33** distinct issues | **10** | **11** | **10** | **2** | — |

**Resolved across all versions:** 18 ✅  
**Partially resolved:** 6 ⚠  
**Open at v5:** 9 ❌
