# UC3 Search – Class Diagram Analysis Report
**File analizzato:** `Correction.puml` (v7)  
**Data analisi:** 2026-03-10  
**Severità:** CRITICAL · HIGH · MEDIUM · LOW  

---

## Sommario Esecutivo

Tutti e 20 i problemi identificati nel round precedente (v6) risultano affrontati in v7.  
L'analisi rileva **4 nuove violazioni critiche**, **7 problemi di alta priorità**, **5 ambiguità di media gravità** e **3 osservazioni minori** — per un totale di **19 issue** introdotte o rimaste irrisolte in questa versione.

| Severità | Conteggio |
|----------|-----------|
| CRITICAL | 4 |
| HIGH | 7 |
| MEDIUM | 5 |
| LOW | 3 |
| **Totale** | **19** |

---

## CRITICAL

### C-1 — `onViewerError()` scrive su `SearchState.error` via facade — `ISearchFacade` non ha tale metodo

La nota di v7 documenta il fix H-5:
> *"onViewerError(err) → searchFacade writes error to SearchState.error via searchFacade"*

`ISearchFacade` espone: `getState()`, `setQuery()`, `setFilters()`, `searchAdvanced()`, `cancelSearch()`, `retry()`.  
Non esiste alcun metodo `setError()`, `reportViewerError()` o equivalente per scrivere un errore esterno nello stato.  
`SearchPageComponent` non può adempiere al comportamento documentato tramite l'interfaccia pubblica — il contratto è impossibile da rispettare senza violare la DIP (iniettare la classe concreta) o rompere l'incapsulamento del facade.

**Fix:** Aggiungere a `ISearchFacade`:
```
+ setViewerError(err: AppError | null): void
```
oppure (preferibile, vedi H-5) separare lo stato dell'errore viewer in un `Signal` locale a `SearchPageComponent`.

---

### C-2 — `IDocumentFacade.loadDocument()` referenzia il tipo `DocumentDetail` — non definito in questo diagramma

Il DTO `DocumentDetail` è stato rimosso esplicitamente:
> *"DocumentDetail removed — MetadataPanelComponent removed (R2-H3); no remaining consumer in this UC diagram."*

Eppure `IDocumentFacade` dichiara ancora:
```
+ loadDocument(documentId: string): Observable<DocumentDetail>
```
Il tipo `DocumentDetail` è un simbolo non risolto in questo diagramma.  
L'interfaccia referenzia un tipo che non esiste nel contesto corrente — il contratto è architetturalmente rotto.

**Fix:** Sostituire con un tipo presente nel diagramma (es. un nuovo DTO `DocumentBlob`) oppure re-inserire `DocumentDetail` come riferimento cross-module nel Shared Kernel.

---

### C-3 — I `provide:` token nel `diTokensNote` usano interfacce TypeScript — cancellate a runtime, il bootstrap fallisce

```
{ provide: ISearchFacade, useClass: SearchFacade }
```

Le interfacce TypeScript sono completamente cancellate dalla compilazione (`tsc`).  
Angular DI richiede come `provide:` un costruttore di classe, una stringa o un'istanza di `InjectionToken<T>`.  
`ISearchFacade` a runtime vale `undefined` — tutte e 11 le entry della nota producono `NullInjectorError` al bootstrap.

**Fix:** Dichiarare token espliciti nel modulo DI:
```typescript
export const SEARCH_FACADE_TOKEN = new InjectionToken<ISearchFacade>('ISearchFacade');
// providers:
{ provide: SEARCH_FACADE_TOKEN, useClass: SearchFacade }
```
Il diagramma deve mostrare i token come elementi separati o documentarne l'esistenza in modo tecnicamente corretto.

---

### C-4 — `DipReadyGuard`: guard funzionale E field injection con classe — contraddizione irrisolvibile

Il body della classe dichiara:
```
- checker: IDipReadyChecker  <<inject>>
```
La nota dichiara:
> *"Angular 17+ functional guard — no class instantiation at runtime. Modelled as class for UML structural clarity only."*

Queste due affermazioni sono mutuamente esclusive.  
Un functional guard usa `inject()` all'interno del corpo della funzione — non esiste alcuna classe, nessun campo, nessuna annotazione `<<inject>>` su un attributo.  
Se è funzionale, il modello corretto è una `<<function>>` con dipendenza da `IDipReadyChecker` espressa come `<<inject>>` call nel corpo, non come campo.  
L'implementatore si trova di fronte a due contratti incompatibili: non può sapere quale realizzare.

**Fix:** Rimuovere il campo `- checker` e documentare il guard come:
```plantuml
class DipReadyGuard <<CanActivateFn>> {
  .. inject(IDipReadyChecker).isReady() ..
}
DipReadyGuard ..> IDipReadyChecker : "<<inject()>>"
```

---

## HIGH

### H-1 — `AppRouter ..> DipReadyGuard : "<<guards route /search>>"` — direzione errata, violazione OCP

`AppRouter` è un adapter su `Router.navigate()`.  
I guard vengono registrati staticamente nella configurazione delle rotte — è l'infrastruttura Angular Router che li invoca, non `AppRouter`.  
Questa freccia significa che ogni volta che viene aggiunto un nuovo guard a qualsiasi rotta, `AppRouter` deve essere modificato — violazione diretta di OCP.  
`AppRouter` non deve conoscere l'esistenza di `DipReadyGuard`.

**Fix:** Rimuovere la freccia `AppRouter ..> DipReadyGuard`. Il guard è dichiarato nella route config (documento statico), non in alcun metodo di `AppRouter`.

---

### H-2 — Entrambi i gateway iniettano `ElectronContextBridge` concreto — violazione DIP + DRY su `invoke()`

`SearchIpcGateway` e `IndexingIpcGateway` dichiarano entrambi:
```
- contextBridge: ElectronContextBridge
```
`ElectronContextBridge` è un tipo concreto senza interfaccia corrispondente (`IElectronContextBridge`). L'intero diagramma è costruito sull'iniezione di astrazioni — questa dipendenza diretta da una classe concreta è un'incoerenza strutturale.  
Inoltre, il metodo privato `invoke<T>()` è duplicato in entrambe le classi con firme diverse (una accetta `AbortSignal`, l'altra no) — violazione DRY con contratto inconsistente.

**Fix:**
- Introdurre `IElectronContextBridge` e farlo iniettare da entrambi i gateway.
- Estrarre `invoke()` in una classe base `BaseIpcGateway` oppure documentare esplicitamente perché le firme differiscono.

---

### H-3 — `DocumentFacade <<Service>>` collocato nel Shared Kernel — contamina il kernel con un'implementazione

Il Shared Kernel deve contenere solo contratti/interfacce cross-cutting (`IDipReadyChecker`).  
`DocumentFacade` è un servizio concreto del bounded context *Document Detail*.  
Inserire una classe concreta di un altro bounded context nel Shared Kernel rompe l'isolamento e crea un accoppiamento trasversale indesiderato.

**Fix:** Spostare `DocumentFacade` in un package separato:
```plantuml
package "External Module References" #F0F0F0 {
  class DocumentFacade <<ExternalModule>> <<Service>> { ... }
}
```

---

### H-4 — `startIndexing()` / `cancelIndexing()` su `SemanticIndexFacade` — API pubblica senza consumer (ISP)

`ISemanticIndexStatus` dichiara solo `getStatus()`.  
`startIndexing()` e `cancelIndexing()` sono metodi pubblici sulla classe concreta ma non appartengono ad alcuna interfaccia e non vengono chiamati da nessun componente in questo diagramma.  
Il commento riconosce che appartengono al modulo DIP Loading, eppure rimangono come metodi pubblici visibili su una classe di questo diagramma — esponendo un'API che nessun consumer in scope può/deve usare.

**Fix:** Rimuovere i metodi da questo diagramma oppure dichiararli dietro un'interfaccia `ISemanticIndexControl` consumata esclusivamente dal modulo DIP Loading (con nota di rimando).

---

### H-5 — `SearchState.error` conflates errori di ricerca ed errori del viewer — retry UI semanticamente errata

Post fix H-5, `onViewerError()` scrive un errore documento in `SearchState.error`.  
Lo stesso campo è letto da `AsyncStateWrapperComponent @Input error` e presenta il pulsante "Riprova" tramite `InlineErrorComponent` (se `error.recoverable === true`).  
Un errore del viewer (es. formato MIME non supportato) attiverebbe la UI di retry della ricerca — comportamento semanticamente sbagliato.  
I due domini di errore sono in conflitto sulla stessa variabile di stato.

**Fix:** Separare lo stato dell'errore viewer in un segnale locale di `SearchPageComponent`:
```
- viewerError: WritableSignal<AppError | null>
```
Non scritto in `SearchState`, non mostrato da `AsyncStateWrapperComponent`.

---

### H-6 — Routing `ValidationResult` → `FilterValueInputComponent` mai modellato

`AdvancedFilterPanelComponent` riceve `@Input validationResult: ValidationResult` dove `errors: Map<string, ValidationError>`.  
Il pannello contiene `CommonFiltersComponent`, `DiDaiFiltersComponent`, `AggregateFiltersComponent`, ognuno con istanze di `FilterValueInputComponent` per ogni campo.  
Come un `ValidationError` per il campo `"startDate"` raggiunge la specifica istanza di `FilterValueInputComponent` non è mai mostrato.  
Nessun `@Input fieldKey` sui componenti filtro, nessun meccanismo di routing mostrato.  
La catena di propagazione dell'errore è architetturalmente mancante.

**Fix:** Aggiungere `@Input fieldKey: string` a `FilterValueInputComponent` e documentare il meccanismo con cui `AdvancedFilterPanelComponent` estrae dal `Map` la `ValidationError` corrispondente e la proietta all'istanza corretta.

---

### H-7 — Doppia scrittura validazione in `FilterValueInputComponent` — locale e facade-autoritativa possono contraddirsi

`FilterValueInputComponent` esegue validazione sincrona locale e:
1. Salva in `lastValidationError`
2. Passa come `@Input` a `FieldErrorComponent`
3. Emette via `@Output validationError` al parent

Il parent emette verso l'alto, `SearchFacade.validate()` produce `ValidationResult`, che viene spinto giù nuovamente a `AdvancedFilterPanelComponent` e dovrebbe raggiungere `FilterValueInputComponent`.  
Due valori indipendenti per lo stesso campo possono coesistere (quello locale e quello autoritativo del facade).  
Nessuna regola specifica quale prevale quando sono in disaccordo (es. validazione locale passa, server-side fallisce).

**Fix:** Documentare la regola di precedenza nella nota del componente:  
> *"Se @Input validationResult contiene un errore per questo fieldKey, sovrascrive lastValidationError."*  
Oppure rimuovere la validazione locale e delegare interamente al facade.

---

## MEDIUM

### M-1 — `SearchBarComponent` assembla `SearchQuery` da testo grezzo — logica di business in un componente Dumb

L'utente digita una stringa libera. `SearchQuery` ha tre campi: `text`, `type: "free"|"className"|"processId"`, `useSemantic: boolean`.  
Il componente emette `@Output queryChanged: EventEmitter<SearchQuery>`.  
La costruzione dell'oggetto `SearchQuery` completo da un `<input>` richiede valori di default per `type` e `useSemantic`.  
Se il componente li hard-code (es. `type: "free"`, `useSemantic: false`), stà prendendo decisioni di dominio — violazione della regola Dumb.  
Nessuna factory, nessun default documentato.

**Fix:** Aggiungere `@Input defaultType: SearchQueryType` e `@Input useSemantic: boolean` al componente, oppure documentare esplicitamente che i default sono costanti UI (non business logic), e quindi accettabili in un Dumb.

---

### M-2 — `setFilters()` raggruppato con dispatch IPC nel label dell'inject — semantica fuorviante

Il label dell'inject su `SearchPageComponent` recita:
> *"dispatches setQuery / setFilters / searchAdvanced / retry"*

`setQuery()`, `searchAdvanced()`, `retry()` attivano chiamate IPC. `setFilters()` esplicitamente non lo fa (memorizza solo).  
Raggrupparli senza qualificazione porta un implementatore a supporre semantica identica — è molto probabile che `setFilters()` venga chiamato aspettandosi una ricerca, o che `searchAdvanced()` non venga mai chiamato perché si crede che `setFilters()` lo faccia già.

**Fix:** Separare nel label:
```
dispatches (IPC): setQuery / searchAdvanced / retry
stores only:      setFilters
```

---

### M-3 — `SearchFacade "1" *-- "1" SearchState` — composizione di un DTO mutabile, semantica UML scorretta

La composizione UML (`*--`) esprime parte-tutto con ciclo di vita dipendente: la parte cessa di esistere quando il tutto cessa.  
`SearchState` come valore di un `WritableSignal` viene *sostituito* (non distrutto) ad ogni aggiornamento di stato.  
La composizione implica che istanze di `SearchState` vengano create e distrutte da `SearchFacade`, il che non corrisponde alla semantica dei Signal di Angular.

**Fix:**
```plantuml
SearchFacade --> SearchState : "WritableSignal<> (current value)"
```
Oppure annotare come campo nel body della classe.

---

### M-4 — Invalidazione cache dopo `abortAndReset()` non specificata — risultati stantii o errati possono essere cachati

`SearchIpcGateway` implementa cache-first con TTL 30s.  
Quando `abortAndReset()` viene chiamato a metà di una chiamata IPC, la chiamata viene abortita.  
Se la cache aveva già memorizzato un risultato parziale o errato per quella chiave nella stessa finestra temporale, la prossima query identica restituisce il risultato sbagliato dalla cache.  
`ICacheService.invalidate(key)` esiste ma non ha nessun caller nel diagramma.

**Fix:** Aggiungere in `abortAndReset()` o in `handleError()` del facade:
> *"Chiama `ICacheService.invalidate(lastQueryKey)` prima di resettare lo stato."*  
E aggiungere la freccia `SearchFacade --> ICacheService : "invalidate on abort"`.

---

### M-5 — Notazione `Signal<SemanticIndexState>.status` nel label dell'inject — accesso al tipo, non al valore

Il label dell'inject recita:
> *"reads Signal<SemanticIndexState>.status"*

`ISemanticIndexStatus.getStatus()` ritorna `Signal<SemanticIndexState>`.  
L'accesso al valore richiede di chiamare il signal: `getStatus()().status`.  
Scrivere `Signal<SemanticIndexState>.status` implica un accesso statico alla proprietà del tipo `Signal` — codice TypeScript non valido che fuorvia l'implementatore.

**Fix:** Correggere il label:
> *"reads getStatus()().status — IndexingStatus"*

---

## LOW

### L-1 — `IRouter.navigate()` accetta `unknown[]` — nessun vincolo sui comandi di navigazione

Angular `Router.navigate()` accetta `any[]`. Usare `unknown[]` è più sicuro ma ancora non tipato.  
Nessun tipo alias o union discriminata (`RouteCommands`) restringe i valori validi.  
Un comando di navigazione sbagliato fallisce silenziosamente a runtime.

---

### L-2 — `SubjectFilterComponent.prevStep()` senza guard al boundary step 1

`nextStep()` non può superare il passo 3; `prevStep()` non può scendere sotto il passo 1.  
Nessuna pre-condizione, guard o nota specifica cosa succede quando `prevStep()` viene chiamato al passo 1 (no-op? throw? reset?).  
Combinato con il `effect()` di sync su `@Input subject`, un reset del parent al passo 3 seguito da un `prevStep()` immediato può produrre transizioni di stato non definite.

---

### L-3 — `SearchResult.score: number` — range e semantica non documentati

`score` guida il ranking della lista risultati. Che si tratti di un valore 0–1 (cosine similarity), 0–100, BM25 illimitato o altro non è specificato.  
Mancano: range, semantica, ordinamento atteso (`DESC`?), valore per assenza di score.  
Questo è un contratto di dominio assente che impatta la logica di display di `SearchResultsComponent`.

---

## Tabella Riepilogativa

| ID | Severità | Titolo |
|----|----------|--------|
| C-1 | **CRITICAL** | `ISearchFacade` manca di metodo per scrivere l'errore viewer |
| C-2 | **CRITICAL** | `IDocumentFacade` referenzia `DocumentDetail` — tipo rimosso, simbolo non risolto |
| C-3 | **CRITICAL** | `provide:` usa interfacce TypeScript — cancellate a runtime, bootstrap fallisce |
| C-4 | **CRITICAL** | `DipReadyGuard` funzionale vs class injection — contraddizione irrisolvibile |
| H-1 | HIGH | `AppRouter ..> DipReadyGuard` — direzione errata, OCP violato |
| H-2 | HIGH | Gateway iniettano `ElectronContextBridge` concreto — DIP + DRY violation |
| H-3 | HIGH | `DocumentFacade` nel Shared Kernel — contamina il kernel con un'implementazione |
| H-4 | HIGH | `startIndexing()` / `cancelIndexing()` senza consumer — dead public API (ISP) |
| H-5 | HIGH | `SearchState.error` conflate search + viewer errors — retry UI sbagliata |
| H-6 | HIGH | Routing `ValidationResult` → `FilterValueInputComponent` mai modellato |
| H-7 | HIGH | Doppia validazione locale + facade — regola di precedenza assente |
| M-1 | MEDIUM | `SearchBarComponent` costruisce `SearchQuery` — business logic in Dumb component |
| M-2 | MEDIUM | `setFilters()` raggruppato con dispatch IPC nel label inject — semantica fuorviante |
| M-3 | MEDIUM | `SearchFacade *-- SearchState` — composizione di DTO mutabile, UML scorretta |
| M-4 | MEDIUM | Cache invalidation su abort non specificata — risultati stantii possibili |
| M-5 | MEDIUM | `Signal<SemanticIndexState>.status` — accesso al tipo, non al valore |
| L-1 | LOW | `IRouter.navigate()` accetta `unknown[]` — nessun vincolo sui comandi |
| L-2 | LOW | `prevStep()` senza boundary guard al passo 1 |
| L-3 | LOW | `SearchResult.score` — range e semantica non documentati |
