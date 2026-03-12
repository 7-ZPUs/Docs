# UC3 Search – Class Diagram Analysis Report
**File analizzato:** `Correction.puml` (v6)  
**Data analisi:** 2026-03-10  
**Severità applicata:** CRITICAL · HIGH · MEDIUM · LOW  

---

## Sommario Esecutivo

Il diagramma presenta **5 violazioni critiche**, **7 problemi di alta priorità**, **5 ambiguità di media gravità** e **3 osservazioni minori**.  
Le issue critiche compromettono la correttezza strutturale e la compilabilità architetturale del diagramma; quelle alte implicano flussi non implementati o contratti rotti che impedirebbero l'implementazione corretta del codice.

| Severità | Conteggio |
|----------|-----------|
| CRITICAL | 5 |
| HIGH | 7 |
| MEDIUM | 5 |
| LOW | 3 |
| **Totale** | **20** |

---

## CRITICAL

### C-1 — `AppRouter` si auto-inietta l'interfaccia che implementa

`AppRouter` dichiara sia `AppRouter ..|> IRouter` (implementazione) sia `- router: IRouter <<inject>>` come campo privato.  
Questo crea una dipendenza circolare: la classe è contemporaneamente il provider e il consumer della stessa astrazione.  

**Corretto:** `AppRouter` deve iniettare il `Router` concreto di `@angular/router`; sono le *altre* classi che iniettano `IRouter`.  

```
ERRATO:  AppRouter ..|> IRouter  +  AppRouter { - router: IRouter }
CORRETTO: AppRouter { - router: Router }  (Angular Router concreto)
          altri componenti iniettano IRouter → fornito da InjectionToken
```

---

### C-2 — `IpcGateway` re-unifica due interfacce segregate per ISP (violazione SRP/ISP)

`ISearchChannel` e `IIndexingChannel` sono state separate esplicitamente per ISP.  
`IpcGateway` implementa entrambe (`IpcGateway ..|> ISearchChannel` + `IpcGateway ..|> IIndexingChannel`) e il body della classe elenca tutti i sei metodi di entrambe le interfacce.  
La segregazione è architetturalmente vuota: un unico adapter riunisce entrambe le responsabilità.

**Corretto:** Introdurre `SearchIpcGateway` e `IndexingIpcGateway` separati, oppure documentare esplicitamente perché la fusione è necessaria (e.g. single `contextBridge` object).

---

### C-3 — Composizione `*--` applicata a un `enum` (`IndexingStatus`)

```plantuml
SemanticIndexState "1" *-- "1"  IndexingStatus
```

`IndexingStatus` è un `enum` — un tipo valore. La composizione UML (`*--`) rappresenta un'istanza con ciclo di vita dipendente. Un enum non ha istanze autonome; è un attributo, non un componente.

**Corretto:**
```plantuml
' Mostrare come attributo nel body della classe, non come composizione
SemanticIndexState : + status: IndexingStatus
```

---

### C-4 — `DipReadyGuard` modellato come `note as`, non come classe

```plantuml
AppRouter --> dipGuardNote : <<guards>>
```

L'arrow punta a un blocco `note as dipGuardNote`. In PlantUML questo non produce una relazione strutturale UML: è puramente decorativo. Il `<<uses>> IDipReadyChecker` esiste solo nella prosa della nota — non è una freccia disegnata.

**Corretto:** Definire `DipReadyGuard` come classe stereotipata e aggiungere la freccia esplicita:
```plantuml
class DipReadyGuard <<CanActivateFn>> {
  + canActivate(): boolean | UrlTree
}
DipReadyGuard ..> IDipReadyChecker : <<uses>>
AppRouter ..> DipReadyGuard : <<guards route /search>>
```

---

### C-5 — Provider di `IDocumentFacade` non visibile; `DocumentViewerComponent` non risolvibile

`DocumentViewerComponent` inietta `IDocumentFacade`, ma il diagramma dichiara solo (in commento):  
> *"IDocumentFacade is implemented by DocumentFacade in the Document Detail module"*

`DocumentFacade` è assente dal diagramma. Nessun `InjectionToken`, nessuna freccia inter-modulo. Dal punto di vista del grafo DI, il binding non esiste: il componente non può essere istanziato.

**Corretto:** Aggiungere almeno un nodo di riferimento cross-module con freccia di dipendenza:
```plantuml
class DocumentFacade <<ExternalModule>> <<Service>>
DocumentFacade ..|> IDocumentFacade
DocumentViewerComponent -[#6B21A8,dashed]-> IDocumentFacade : <<inject>>
```

---

## HIGH

### H-1 — `SearchState.loading` e `SearchState.isSearching` ridondanti (DRY)

Entrambi i campi sono `boolean` senza distinzione documentata. `AsyncStateWrapperComponent` ha `@Input loading: boolean` — non è chiaro quale dei due vi sia mappato. Due campi per lo stesso concetto generano incoerenza nello stato proiettato.

**Corretto:** Rimuovere uno dei due oppure documentare la distinzione precisa nel DTO (es. `loading = attesa risposta IPC`, `isSearching = mutex che include debounce`).

---

### H-2 — `setQuery()` non specifica auto-cancellazione sulle chiamate concorrenti

La nota documenta "abort su `cancelSearch()`/`retry()`", ma non su `setQuery()`. Se l'utente digita due caratteri prima che la prima IPC call si risolva, esistono due `Observable` in volo che possono produrre race condition e risultati stantii che sovrascrivono quelli freschi.

**Corretto:** Specificare nel contratto di `ISearchFacade.setQuery()`:  
> *"Se `isSearching === true`, chiama `abortAndReset()` prima di avviare la nuova ricerca."*

---

### H-3 — Trigger di `IFilterValidator.validate()` mai descritto

`SearchFacade` inietta `IFilterValidator` e `SearchState.validationResult: ValidationResult` viene popolato da qualche parte. Ma nessun metodo, freccia di flusso o hook descrive *quando* la validazione viene invocata.  
`AdvancedFilterPanelComponent` dipende da `@Input validationResult` già popolato — la sorgente è architecturally invisibile.

**Corretto:** Aggiungere esplicitamente nel contratto di `setFilters()` o `searchAdvanced()`:  
> *"Chiama `IFilterValidator.validate(filters)` → aggiorna `SearchState.validationResult`."*

---

### H-4 — `empty: boolean` su `AsyncStateWrapperComponent` senza origine modellata

`SearchState` non ha un campo `empty`. `SearchPageComponent` deve derivarlo (`results.length === 0 && !loading && !error`) e passarlo come `@Input`. Questa logica di proiezione non è in alcuna classe, attributo o freccia.

**Corretto:** Aggiungere a `SearchPageComponent`:
```
~ isEmpty: Signal<boolean>  [derived: results().length === 0 && !loading()]
```

---

### H-5 — `onViewerError(AppError)` senza effetto documentato

`DocumentViewerComponent.@Output viewerError` è ricevuto da `SearchPageComponent.onViewerError()`. Il metodo esiste ma non ha frecce downstream: nessuna notifica, nessuna scrittura a `SearchState.error`, nessun `ErrorDialog`. Il flusso termina nel vuoto.

**Corretto:** Documentare l'effetto: es. `onViewerError()` → `errorDialog.open(err)` oppure `→ selectedDocumentId.set(null)`.

---

### H-6 — `SubjectFilterComponent` Signals interni non sincronizzati con `@Input subject`

I `WritableSignal` interni (`currentStep`, `selectedRole`, `selectedType`) sono inizializzati a valori di default ma non è descritto nessun meccanismo reattivo (Angular `effect()`, `ngOnChanges`) che li sincronizzi quando il parent cambia `@Input subject` (es. reset filtri). Il wizard può divergere dall'`@Input`.

**Corretto:** Documentare:  
> *"`effect(() => { if (this.subject()) { this.populateFromInput(); } })`"*

---

### H-7 — `ISearchChannel.search()` e `searchSemantic()` privi di `AbortSignal`

`searchAdvanced(f, s: AbortSignal)` supporta la cancellazione IPC. `search(q)` e `searchSemantic(q)` no. Se `cancelSearch()` viene invocato durante una full-text search, l'interfaccia non offre meccanismo di abort: la chiamata IPC rimane in volo.

**Corretto:**
```plantuml
+ search(q: SearchQuery, s: AbortSignal): Observable<SearchResult[]>
+ searchSemantic(q: SearchQuery, s: AbortSignal): Observable<SearchResult[]>
```

---

## MEDIUM

### M-1 — `setFilters()` vs `searchAdvanced()` — firme identiche, semantica ambigua

Entrambi i metodi su `ISearchFacade` accettano `SearchFilters`. Non è specificato se `setFilters()` salva solo lo stato (senza trigger IPC) oppure esegue anche la ricerca. L'inject label di `SearchPageComponent` li elenca entrambi senza regole d'uso.

**Corretto:** Documentare nel contratto:  
- `setFilters()` → aggiorna solo `SearchState.filters` (nessuna IPC call)  
- `searchAdvanced()` → valida + esegue IPC call searchAdvanced

---

### M-2 — Freccia `SearchFacade --> SearchState : "emits Signal<>"` inverte la proprietà

`SearchFacade` *possiede* un `WritableSignal<SearchState>` come campo privato. Non "emette verso" `SearchState`. La freccia suggerisce che `SearchState` sia un sink/subscriber, invertendo la realtà.

**Corretto:** Modellare come composizione o campo:
```plantuml
SearchFacade "1" *-- "1" SearchState : "owns WritableSignal<>"
```

---

### M-3 — `InjectionToken` Angular assenti — wire-up DI non verificabile

I componenti Smart iniettano interfacce (`ISearchFacade`, `ISemanticIndexStatus`, ecc.) ma in Angular le interfacce non sono iniettabili senza un `InjectionToken<T>`. Nessun token è mostrato, nessun `provide` è dichiarato. Il collegamento `ISearchFacade → SearchFacade` è affermato testualmente ma non è architetturalmente verificabile.

---

### M-4 — `AdvancedFilterPanelComponent <<Dumb>>` con metodi mutativi ambigui

`addFilter()`, `removeFilter()`, `resetFilters()` sono elencati come metodi su un componente `<<Dumb>>`. Se modificano stato locale, violano la regola Dumb. Se calcolano un nuovo valore e emettono `@Output`, sono corretti ma questo non è specificato.

**Corretto:** Chiarire che i metodi sono helper puri:  
> *"Computano il nuovo `SearchFilters` e emettono `filtersChanged` — nessuno stato locale modificato."*

---

### M-5 — Stato effimero in `FilterValueInputComponent` non documentato

Il componente emette `@Output validationError` verso il parent E passa `ValidationError` come `@Input` al proprio child `FieldErrorComponent`. Per fare entrambe le cose deve mantenere il risultato della validazione tra un cambiamento dell'input e l'emissione dell'output. Questo stato effimero non è documentato, contraddicendo la dichiarazione "no side-effects".

---

## LOW

### L-1 — Re-render loop `SearchBarComponent @Input query` non gestito

Il flusso unidirezionale produce: keystroke → `@Output queryChanged` → `SearchFacade.setQuery()` → Signal aggiornato → `@Input query` aggiornato da Smart → `SearchBarComponent` re-renderizzato. Se Angular sostituisce il valore del `<input>` nel DOM, la posizione del cursore dell'utente viene persa. Il pattern "controlled input" vs. "uncontrolled input" in Angular non è menzionato.

---

### L-2 — Helper privati nel class box di `SearchFacade`

`createAbortController()`, `abortAndReset()`, `handleError()`, `resetSearching()` sono elencati nel class box. I diagrammi UML convenzionalmente omettono i dettagli implementativi privati dalla superficie di interfaccia. Questi appartengono alla nota (che li descrive già), non al box.

---

### L-3 — `retry()` con no-op silenzioso delega al caller l'ispezione dello stato

Il contratto di `ISearchFacade.retry()` specifica: *"No-op se `SearchState` non contiene query precedente."* Il caller deve leggere `getState()` prima di chiamare `retry()` per evitare behavior vuoto. Questo crea un coupling implicito che non è espresso nella firma del metodo.

**Corretto:** `retry(): boolean` (ritorna `false` se no-op) oppure `retry(): void` con precondizione documentata che il caller è tenuto a verificare.

---

## Tabella Riepilogativa

| ID | Severità | Titolo |
|----|----------|--------|
| C-1 | **CRITICAL** | `AppRouter` auto-inietta `IRouter` che implementa |
| C-2 | **CRITICAL** | `IpcGateway` re-unifica `ISearchChannel` + `IIndexingChannel` (SRP/ISP) |
| C-3 | **CRITICAL** | Composizione `*--` su enum `IndexingStatus` |
| C-4 | **CRITICAL** | `DipReadyGuard` è una `note`, non una classe UML |
| C-5 | **CRITICAL** | Provider `IDocumentFacade` assente; `DocumentViewerComponent` non risolvibile |
| H-1 | HIGH | `SearchState.loading` / `isSearching` ridondanti |
| H-2 | HIGH | `setQuery()` non specifica auto-cancellazione concorrente |
| H-3 | HIGH | Trigger `IFilterValidator.validate()` non modellato |
| H-4 | HIGH | Origine di `empty: boolean` non modellata |
| H-5 | HIGH | `onViewerError()` senza effetto downstream |
| H-6 | HIGH | `SubjectFilterComponent` Signals interni non sincronizzati con `@Input` |
| H-7 | HIGH | `search()` / `searchSemantic()` privi di `AbortSignal` |
| M-1 | MEDIUM | `setFilters()` vs `searchAdvanced()` semantica ambigua |
| M-2 | MEDIUM | Freccia `SearchFacade --> SearchState` inverte la proprietà |
| M-3 | MEDIUM | `InjectionToken` Angular assenti |
| M-4 | MEDIUM | Metodi mutativi su `AdvancedFilterPanelComponent <<Dumb>>` ambigui |
| M-5 | MEDIUM | Stato effimero in `FilterValueInputComponent` non documentato |
| L-1 | LOW | Re-render loop `SearchBarComponent @Input query` |
| L-2 | LOW | Helper privati nel class box di `SearchFacade` |
| L-3 | LOW | `retry()` no-op silenzioso delega ispezione al caller |
