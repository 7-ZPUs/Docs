### **1. ENTITÀ (core/domain/entities)**

| Entità | Descrizione | Value Objects correlati |
|--------|-------------|------------------------|
| **DIP** | Pacchetto di disseminazione (root) | `DipUUID`, `DipPath` |
| **DocumentClass** | Classificazione documentale | `DocumentClassId`, `DocumentClassName` |
| **AIP** | Archival Information Package | `AipUUID`, `AipRoot` |
| **Document** | Documento archivistico | `DocumentPath` |
| **File** | File fisico (primary/attachment) | `FilePath`, `FileHash` |
| **Metadata** | Metadato chiave-valore | `MetaType` (string/number/date) |
| **Subject** | Soggetto (persona/ente) | Sottotipi: `SubjectPF`, `SubjectPG`, `SubjectPAI`, `SubjectPAE`, `SubjectAS`, `SubjectSQ` |
| **AdministrativeProcedure** | Procedimento amministrativo | `AdministrativeProcedureId`, `AdministrativeProcedureName` |
| **Phase** | Fase del procedimento | `DateRange` |
| **DocumentAggregation** | Aggregazione di documenti | |
| **ArchivalProcess** | Processo archivistico | |
| **FileIntegrityCheck** | Risultato verifica hash | `HashAlgorithm`, `HashValue` |
| **SemanticVector** | Embedding per ricerca AI | `VectorEmbedding(384 dim)` |

---

### **2. USE CASES (core/application/use-cases)**

| Use Case | Input | Output | Descrizione |
|----------|-------|--------|-------------|
| **IndexDIP** | | `IndexResult` | Legge DiPIndex.xml, parsa struttura ed estrae metadati/file in DB |
| **SearchClassiDocumentali** | `filters[]`, `searchName` | `ClasseDocumentale[]` | Ricerca per metadata con filtri AND |
| **SearchProcessi** | `filters[]`, `searchName` | `Processo[]` | Ricerca per metadata con filtri AND |
| **SearchDocuments** | `filters[]`, `searchName` | `Documento[]` | Ricerca per metadata con filtri AND |
| **SearchSemantic** | `query: string` | `{id, score}[]` | Ricerca semantica via AI (similarità vettoriale) |
| **GetClasseDocumentaleById** | `id: string` | `DocumentClass` | Recupera una classe documentale per ID |
| **GetProcessoById** | `id: string` | `Process` | Recupera un processo per ID |
| **GetDocumentoById** | `id: string` | `Document` | Recupera un documento per ID |
| **GetFileById** | `id: string` | `File` | Recupera un file per ID |
| **CheckDIPIntegrity** | `Id` | `IntegrityCheckResult` | Calcola SHA256 e confronta con hash atteso (Impronta) |
| **CheckClasseDocumentaleIntegrity** | `Id` | `IntegrityCheckResult` | Calcola SHA256 e confronta con hash atteso (Impronta) |
| **CheckProcessoIntegrity** | `Id` | `IntegrityCheckResult` | Calcola SHA256 e confronta con hash atteso (Impronta) |
| **CheckFileIntegrity** | `Id` | `IntegrityCheckResult` | Calcola SHA256 e confronta con hash atteso (Impronta) |
| **GetClassiDocumentaliByStatus** | `Id` | `ClasseDocumentale[]` | Ritorna la lista delle classi documentali con lo status specificato |
| **GetProcessiByStatus** | `Id` | `Processo[]` | Ritorna la lista dei processi con lo status specificato |
| **GetDocumentiByStatus** | `Id` | `Documento[]` | Ritorna la lista dei documenti con lo status specificato |
| **GetFilesByStatus** | `Id` | `File[]` | Ritorna la lista dei file con lo status specificato |
| **OpenFile** | `Id` | void | Apre file con app di sistema o finestra Electron |
| **ExportFile** | `Id`, `targetPath` | `ExportResult` | Salva file su disco utente |

---

### **3a. PORTS (core/domain/ports)**
| Port | Metodi principali |
|------|-------------------|
| **WordEmbeddingPort** | `generateEmbedding(text: string): Promise<Vector>` |
| **PackageReaderPort** | `getDipIndex(): Promise<XmlString>`, `getPindexByUuid(process_uuid)`, `getAiPInfoByUuid(aip_uuid)`, `getDocumentMetadata(document_uuid)`, `getFileContent(file_uuid)`, `readFileBytes(file_id)`, `openReadStream(file_id)` |
| **FileExportPort** | `exportFile(destPath: string, content: Buffer): Promise<ExportResult>`, `openWriteStream(destPath: string, source: Readable): Promise<void>` |
| **PrintPort** | `printFile(buffer: Buffer): Promise<PrintResult>, printFileStream(source: Readable): Promise<void>` |
---

### **3b. REPOSITORY (core/domain/repositories - interfaces)**

| Repository | Metodi principali |
|------------|-------------------|
| **DipRepository** | `get(uuid)`, `create(uuid)`, `list()`, `delete(uuid)` |
| **ClasseDocumentaleRepository** | `get(uuid)`, `create(uuid)`, `list()`, `delete(uuid)` |
| **ProcessoRepository** | `get(uuid)`, `create(uuid)`, `list()`, `delete(uuid)` |
| **DocumentoRepository** | `get(uuid)`, `create(uuid)`, `list()`, `delete(uuid)` |
| **FileRepository** | `get(uuid)`, `create(uuid)`, `list()`, `delete(uuid)` |
| **SubjectRepository** | `findById(id)`, `findByDocument(docId)`, `save(subject)` |
| **PhaseRepository** | `findById(id)`, `findByDocument(docId)`, `save(subject)` |
| **VectorRepository** | `save(docId, vector)`, `search(queryVector, limit)`, `getAll()`, `clear()` |
---

### **4. ADAPTER (core/infrastructure/adapters)**

| Adapter | Tipo | Implementa |
|---------|------|------------|
| **SQLiteDipRepository** | Persistence | `DipRepository` - usa better-sqlite3 |
| **SQLiteClasseDocumentaleRepository** | Persistence | `ClasseDocumentaleRepository` |
| **SQLiteProcessoRepository** | Persistence | `ProcessoRepository` |
| **SQLiteDocumentoRepository** | Persistence | `DocumentoRepository` |
| **SQLiteFileRepository** | Persistence | `FileRepository` |
| **SQLiteSubjectRepository** | Persistence | `SubjectRepository` |
| **SQLitePhaseRepository** | Persistence | `PhaseRepository` |
| **SQLiteVectorRepository** | Persistence | `VectorRepository` - con fallback BLOB se vss non disponibile |
| **TransformersJSEmbeddingAdapter** | AI | Adapter per `WordEmbeddingPort` con `@xenova/transformers` (paraphrase-multilingual-MiniLM-L12-v2) |
| **FileSystemPackageReaderAdapter** | IO | Adapter per `PackageReaderPort` |
| **FileSystemExportAdapter** | IO | Adapter per `FileExportPort` |
| **PrinterPrintPortAdapter** | IO | Adapter per `PrintPort` |

---

### **5. IPC ADAPTER (core/infrastructure/ipc)**

#### DIP

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `dip:get-tree-DIP` | - | `FileNode[]` | Albero gerarchico DIP |
| `dip:check-integrity` | `dipUUID: string` | `IntegrityCheckResult` | Verifica integrità DIP |

#### Classe Documentale

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `classe:get-by-id` | `id: string` | `DocumentClass` | Recupera classe per ID |
| `classe:search` | `name?: string` | `DocumentClass[]` | Ricerca con filtri |
| `classe:get-by-status` | `status: string` | `DocumentClass[]` | Lista per stato integrità |
| `classe:check-integrity` | `id: string` | `IntegrityCheckResult` | Verifica integrità classe |

#### Processo

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `processo:get-by-id` | `id: string` | `ArchivalProcess` | Recupera processo per ID |
| `processo:search` | `name?: string` | `ArchivalProcess[]` | Ricerca con filtri |
| `processo:get-by-status` | `status: string` | `ArchivalProcess[]` | Lista per stato integrità |
| `processo:check-integrity` | `id: string` | `IntegrityCheckResult` | Verifica integrità processo |

#### Documento

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `documento:get-by-id` | `id: string` | `Document` | Recupera documento per ID |
| `documento:search` | `filters: SearchFilter[]` | `Document[]` | Ricerca con filtri |
| `documento:get-metadata` | `documentId: number` | `Metadata[]` | Metadati documento |

#### File

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `file:get-by-id` | `id: string` | `File` | Recupera file per ID |
| `file:get-by-document` | `documentId: number` | `File[]` | File di un documento |
| `file:get-path` | `fileId: number` | `string` | Percorso fisico file |
| `file:get-metadata` | `fileId: number` | `Metadata[]` | Metadati file |
| `file:open-external` | `path: string` | `{ success: boolean }` | Apre con app sistema |
| `file:open-in-window` | `path: string` | `{ success: boolean }` | Apre in finestra Electron |
| `file:print` | `fileId: number, targetPath?: string` | `{ success: boolean; savedPath?: string }` | Stampa file (con dialog) |
| `file:download` | `fileId: number, targetPath?: string` | `{ success: boolean; savedPath?: string }` | Salva file (con dialog) |
| `file:check-integrity` | `fileId: number` | `IntegrityCheckResult` | Verifica hash file e ritorna il risultato |
| `file:get-integrity-status` | `fileId: number` | `SavedIntegrityStatus \| null` | Stato integrità salvato |

#### AI / Ricerca Semantica

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `ai:state` | - | `{ initialized: boolean; indexedDocuments: number }` | Stato modello AI |
| `ai:search` | `query: string` | `SearchResult[]` | Ricerca semantica |

#### Filtri / Ricerca

| Canale IPC | Input | Output | Descrizione |
|------------|-------|--------|-------------|
| `search:metadata` | `filters: SearchFilter[]` | `FileNode[]` | Ricerca per metadata con filtri AND |
