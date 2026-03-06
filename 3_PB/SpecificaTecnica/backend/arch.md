# MVP DIP Reader - Architettura Clean Architecture

> Documento generato dall'analisi del PoC per guidare lo sviluppo del MVP

## Struttura Repository MVP

```
mvp/
├── root/                    # Orchestration (entrypoint Electron, config)
├── core/                    # Backend Electron + Domain (Clean Architecture)
│   ├── entity/
│   ├── ipc/            # IPC handlers/adapters
|   ├── repo/           # Interfaces
│   │   └── impl/
│   ├── use-case/
│   │   └── impl/
│   └── value-objects/
├── renderer/               # Angular UI
│   └── src/app/
│       ├── features/       # Feature modules
│       ├── services/       # API services (IPC bridge)
│       └── shared/         # Shared components
└── shared/                 # Contratti cross-layer
    ├── ipc-channels.ts
    ├── types/
    └── errors/
```

---

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

---

### **6. CONTRATTI CONDIVISI (shared/)**

```typescript
// shared/ipc-channels.ts
export const IpcChannels = {
  DB_INIT: 'db:init',
  DB_OPEN: 'db:open',
  DB_INDEX: 'db:index',
  // ... etc
} as const;

// shared/types/dip.types.ts
export interface FileNode { name, type, children, fileId?, documentId?, expanded? }
export interface IntegrityCheckResult { isValid, calculatedHash, expectedHash }
export interface SearchFilter { key: string; value: string }
export interface FilterOptionGroup { groupLabel, groupPath, options[] }
export interface IndexResult { success, dipUUID, semanticIndexed, semanticTotal }
```

---

### **7. COMPONENTI UI (renderer/src/app/)**

| Componente/Feature | Responsabilità |
|--------------------|----------------|
| **AppComponent** | Shell principale, gestisce tree navigazione, search, selezione file |
| **MetadataViewerComponent** | Visualizza metadati di file/documento selezionato |
| **FileTreeComponent** *(da estrarre)* | Albero navigabile gerarchico |
| **SearchFiltersComponent** *(da estrarre)* | UI filtri metadata con gruppi |
| **SemanticSearchComponent** *(da estrarre)* | Input query AI + risultati |
| **IntegrityStatusComponent** *(da estrarre)* | Badge/stato verifica hash |

**Servizi Angular (renderer/src/app/services/):**

| Servizio | Funzione |
|----------|----------|
| `DatabaseService` | Proxy verso IPC per tutte le operazioni DB |
| `SearchService` | Ricerca metadata + semantica |
| `MetadataService` | Accesso metadati file/documento |
| `FileService` | Path fisici, subjects, procedures |
| `FileIntegrityService` | Verifica e salvataggio integrità hash |

---

## ENTITÀ (Ordine di Sviluppo)



Le entità sono ordinate per dipendenza: sviluppa prima quelle senza dipendenze esterne.

### Fase 1 - Entità Base (Nessuna Dipendenza)

#### 1.1 DocumentClass
```typescript
// core/domain/entities/document-class.entity.ts
interface DocumentClass {
  id: number;
  className: string;
}
```

#### 1.2 ArchivalProcess
```typescript
// core/domain/entities/archival-process.entity.ts
interface ArchivalProcess {
  uuid: string;  // UUID v4
}
```

#### 1.3 Subject (Base)
```typescript
// core/domain/entities/subject.entity.ts
interface Subject {
  id: number;
  type: SubjectType;
}

type SubjectType = 'PF' | 'PG' | 'PAI' | 'PAE' | 'AS' | 'SQ';
```

#### 1.4 AdministrativeProcedure
```typescript
// core/domain/entities/administrative-procedure.entity.ts
interface AdministrativeProcedure {
  id: number;
  catalogUri: string;
  title: string;
  subjectOfInterest?: string;
}
```

---

### Fase 2 - Entità con Dipendenze Semplici

#### 2.1 Subject Specializations
```typescript
// core/domain/entities/subjects/

// Persona Fisica
interface SubjectPF extends Subject {
  cf?: string;           // Codice Fiscale (11 chars)
  firstName: string;
  lastName: string;
  digitalAddresses?: string;
}

// Persona Giuridica
interface SubjectPG extends Subject {
  pIva?: string;         // Partita IVA (11 chars)
  companyName: string;
  officeName?: string;
  digitalAddresses?: string;
}

// Pubblica Amministrazione Italiana
interface SubjectPAI extends Subject {
  administrationIpaName: string;
  administrationAooName: string;
  administrationUorName: string;
  digitalAddresses?: string;
}

// Pubblica Amministrazione Estera
interface SubjectPAE extends Subject {
  administrationName: string;
  officeName?: string;
  digitalAddresses?: string;
}

// Altro Soggetto
interface SubjectAS extends Subject {
  firstName?: string;
  lastName?: string;
  cf?: string;
  organizationName: string;
  officeName: string;
  digitalAddresses?: string;
}

// Sistema/Software
interface SubjectSQ extends Subject {
  systemName: string;
}
```

#### 2.2 Phase
```typescript
// core/domain/entities/phase.entity.ts
interface Phase {
  id: number;
  type: string;
  startDate: Date;
  endDate?: Date;
  administrativeProcedureId: number;
}
```

#### 2.3 DocumentAggregation
```typescript
// core/domain/entities/document-aggregation.entity.ts
interface DocumentAggregation {
  id: number;
  procedureId?: number;
  type: string;          // Max 70 chars
}
```

---

### Fase 3 - Entità Core (Dipendenze Multiple)

#### 3.1 AIP (Archival Information Package)
```typescript
// core/domain/entities/aip.entity.ts
interface AIP {
  uuid: string;
  documentClassId?: number;
  archivalProcessUuid?: string;
  rootPath: string;
}
```

#### 3.2 Document
```typescript
// core/domain/entities/document.entity.ts
interface Document {
  id: number;
  rootPath: string;
  aipUuid: string;
  aggregationId?: number;
}
```

#### 3.3 File
```typescript
// core/domain/entities/file.entity.ts
interface File {
  id: number;
  relativePath: string;
  rootPath: string;
  isMain: boolean;
  documentId: number;
}
```

#### 3.4 Metadata
```typescript
// core/domain/entities/metadata.entity.ts
interface Metadata {
  id: number;
  metaKey: string;
  metaValue: string;
  metaType: MetaType;
  documentId?: number;
  fileId?: number;
  aipUuid?: string;
  archivalProcessUuid?: string;
}

type MetaType = 'string' | 'number' | 'date';
```

---

### Fase 4 - Entità di Supporto

#### 4.1 FileIntegrityCheck
```typescript
// core/domain/entities/file-integrity-check.entity.ts
interface FileIntegrityCheck {
  id: number;
  fileId: number;
  result: boolean;
  algorithm: string;      // 'SHA-256'
  dateCalculated: Date;
}
```

#### 4.2 SemanticVector
```typescript
// core/domain/entities/semantic-vector.entity.ts
interface SemanticVector {
  documentId: number;
  embedding: Float32Array;  // 384 dimensions
}
```

#### 4.3 DocumentSubjectAssociation (Join Table)
```typescript
// core/domain/entities/document-subject-association.entity.ts
interface DocumentSubjectAssociation {
  documentId: number;
  subjectId: number;
}
```

---

## VALUE OBJECTS

```typescript
// core/domain/value-objects/

// UUID validato
class DipUUID {
  private constructor(private readonly value: string) {}
  
  static create(value: string): DipUUID {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(value)) throw new InvalidUUIDError(value);
    return new DipUUID(value);
  }
  
  toString(): string { return this.value; }
}

// Path normalizzato
class FilePath {
  private constructor(private readonly value: string) {}
  
  static create(value: string): FilePath {
    const normalized = value
      .replace(/\\/g, '/')
      .replace(/^\.\//, '')
      .replace(/\/+/g, '/');
    return new FilePath(normalized);
  }
  
  toString(): string { return this.value; }
}

// Hash crittografico
class FileHash {
  constructor(
    readonly value: string,
    readonly algorithm: HashAlgorithm = 'SHA-256'
  ) {}
  
  equals(other: FileHash): boolean {
    return this.value === other.value && this.algorithm === other.algorithm;
  }
}

type HashAlgorithm = 'SHA-256' | 'SHA-1' | 'MD5';

// Range di date
class DateRange {
  constructor(
    readonly start: Date,
    readonly end?: Date
  ) {
    if (end && start > end) throw new InvalidDateRangeError();
  }
  
  isActive(): boolean {
    return !this.end || this.end > new Date();
  }
}
```

---

## USE CASES (Ordine di Sviluppo)

### Fase 1 - Core CRUD

| # | Use Case | Input | Output | Priorità |
|---|----------|-------|--------|----------|
| 1 | **ListDatabases** | - | `string[]` | Alta |
| 2 | **OpenDatabase** | `dipUUID` | `DatabaseInfo` | Alta |
| 3 | **DeleteDatabase** | `dipUUID` | `boolean` | Media |
| 4 | **ExportDatabase** | `targetPath?` | `ExportResult` | Bassa |

### Fase 2 - Indexing

| # | Use Case | Input | Output | Priorità |
|---|----------|-------|--------|----------|
| 5 | **IndexDIP** | `dipPath`, `dipUUID` | `IndexResult` | Alta |
| 6 | **GenerateSemanticEmbeddings** | - | `{indexed, total}` | Media |

### Fase 3 - Query & Search

| # | Use Case | Input | Output | Priorità |
|---|----------|-------|--------|----------|
| 7 | **GetFileTree** | - | `FileNode[]` | Alta |
| 8 | **GetMetadata** | `fileId` / `documentId` | `Metadata[]` | Alta |
| 9 | **SearchDocuments** | `filters[]`, `name?` | `FileNode[]` | Alta |
| 10 | **SearchSemantic** | `query: string` | `{id, score}[]` | Media |

### Fase 4 - File Operations

| # | Use Case | Input | Output | Priorità |
|---|----------|-------|--------|----------|
| 11 | **GetFilePath** | `fileId` | `string` | Alta |
| 12 | **OpenFile** | `fileId` | void | Alta |
| 13 | **DownloadFile** | `fileId`, `targetPath` | `SaveResult` | Media |
| 14 | **VerifyFileIntegrity** | `fileId` | `IntegrityCheckResult` | Media |

---

## REPOSITORY INTERFACES

```typescript
// core/domain/repositories/

interface DipRepository {
  open(uuid: string): Promise<OpenDatabaseResult>;
  create(uuid: string): Promise<OpenDatabaseResult>;
  list(): string[];
  delete(uuid: string): { success: boolean };
  export(targetPath: string): { success: boolean; path?: string };
  getInfo(): DatabaseInfo;
}

interface DocumentRepository {
  findById(id: number): Promise<Document | null>;
  findByAip(aipUuid: string): Promise<Document[]>;
  save(doc: Document): Promise<number>;
  searchByMetadata(filters: SearchFilter[]): Promise<Document[]>;
}

interface FileRepository {
  findById(id: number): Promise<File | null>;
  findByDocument(documentId: number): Promise<File[]>;
  getPhysicalPath(fileId: number): Promise<string | null>;
  save(file: File): Promise<number>;
}

interface MetadataRepository {
  findByFile(fileId: number): Promise<Metadata[]>;
  findByDocument(documentId: number): Promise<Metadata[]>;
  save(metadata: Metadata): Promise<number>;
  getDistinctKeys(): Promise<string[]>;
  findByKey(key: string, value: string): Promise<Metadata[]>;
}

interface VectorRepository {
  save(documentId: number, vector: Float32Array): void;
  search(queryVector: Float32Array, limit: number): { id: number; score: number }[];
  getAll(): { id: number }[];
  clear(): void;
}

interface IntegrityRepository {
  save(fileId: number, result: IntegrityCheckResult): Promise<void>;
  findByFile(fileId: number): Promise<SavedIntegrityStatus | null>;
}

interface SubjectRepository {
  findById(id: number): Promise<Subject | null>;
  findByDocument(documentId: number): Promise<Subject[]>;
  save(subject: Subject): Promise<number>;
}
```

---

## INFRASTRUCTURE ADAPTERS

### Persistence (SQLite)

| Adapter | Implementa | Note |
|---------|------------|------|
| `SQLiteDipRepository` | `DipRepository` | better-sqlite3, gestione multi-DB |
| `SQLiteDocumentRepository` | `DocumentRepository` | |
| `SQLiteFileRepository` | `FileRepository` | |
| `SQLiteMetadataRepository` | `MetadataRepository` | |
| `SQLiteVectorRepository` | `VectorRepository` | sqlite-vss con fallback BLOB |
| `SQLiteIntegrityRepository` | `IntegrityRepository` | |
| `SQLiteSubjectRepository` | `SubjectRepository` | |

### Parsers

| Adapter | Funzione |
|---------|----------|
| `XmlDipIndexParser` | Parsing DiPIndex.xml (xmldom) |
| `XmlMetadataParser` | Parsing metadata XML per documento |

### AI/Embedding

| Adapter | Funzione |
|---------|----------|
| `TransformersEmbeddingService` | @xenova/transformers, modello paraphrase-multilingual-MiniLM-L12-v2 |

### Infrastructure Services

| Service | Funzione |
|---------|----------|
| `FilesystemService` | Lettura/scrittura file, verifica esistenza |
| `HashingService` | SHA256 via Web Crypto API |
| `DialogService` | Electron dialogs (open, save) |

---

## IPC CHANNELS (shared/)

```typescript
// shared/ipc-channels.ts
export const IpcChannels = {
  // Database
  DB_INIT: 'db:init',
  DB_OPEN: 'db:open',
  DB_INDEX: 'db:index',
  DB_QUERY: 'db:query',
  DB_LIST: 'db:list',
  DB_DELETE: 'db:delete',
  DB_EXPORT: 'db:export',
  DB_INFO: 'db:info',
  
  // DIP
  DIP_SELECT_DIRECTORY: 'dip:select-directory',
  
  // File
  FILE_READ: 'file:read',
  FILE_OPEN_EXTERNAL: 'file:open-external',
  FILE_OPEN_IN_WINDOW: 'file:open-in-window',
  FILE_DOWNLOAD: 'file:download',
  
  // AI
  AI_INIT: 'ai:init',
  AI_INDEX: 'ai:index',
  AI_GENERATE_EMBEDDING: 'ai:generate-embedding',
  AI_SEARCH: 'ai:search',
  AI_REINDEX_ALL: 'ai:reindex-all',
  AI_STATE: 'ai:state',
  AI_CLEAR: 'ai:clear',
  
  // Utils
  DIALOG_SHOW_MESSAGE: 'dialog:show-message',
} as const;

export type IpcChannel = typeof IpcChannels[keyof typeof IpcChannels];
```

---

## SHARED TYPES

```typescript
// shared/types/

// File Tree Node
export interface FileNode {
  name: string;
  type: 'folder' | 'file';
  children: FileNode[];
  expanded?: boolean;
  fileId?: number;
  documentId?: number;
}

// Search
export interface SearchFilter {
  key: string;
  value: string;
}

export interface FilterOptionGroup {
  groupLabel: string;
  groupPath: string;
  options: Array<{ value: string; label: string }>;
}

// Integrity
export interface IntegrityCheckResult {
  isValid: boolean;
  calculatedHash: string;
  expectedHash: string;
}

export interface SavedIntegrityStatus {
  verifiedAt: string;
  algorithm: string;
  result: boolean;
}

export type IntegrityStatus = 'none' | 'loading' | 'valid' | 'invalid' | 'error';

// Database
export interface DatabaseInfo {
  open: boolean;
  dipUUID?: string;
  fileCount?: number;
  documentCount?: number;
  vectorCount?: number;
  vssEnabled?: boolean;
}

export interface OpenDatabaseResult {
  success: boolean;
  dipUUID: string;
  existed: boolean;
}

export interface IndexResult {
  success: boolean;
  dipUUID: string;
  semanticIndexed: number;
  semanticTotal: number;
}

// AI Search
export interface SemanticSearchResult {
  id: number;
  score: number;
}
```

---

## SHARED ERRORS

```typescript
// shared/errors/

export class DomainError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class InvalidUUIDError extends DomainError {
  constructor(value: string) {
    super(`Invalid UUID format: ${value}`);
  }
}

export class InvalidDateRangeError extends DomainError {
  constructor() {
    super('End date cannot be before start date');
  }
}

export class DipNotFoundError extends DomainError {
  constructor(uuid: string) {
    super(`DIP not found: ${uuid}`);
  }
}

export class FileNotFoundError extends DomainError {
  constructor(path: string) {
    super(`File not found: ${path}`);
  }
}

export class IntegrityMismatchError extends DomainError {
  constructor(expected: string, calculated: string) {
    super(`Hash mismatch. Expected: ${expected}, Calculated: ${calculated}`);
  }
}

export class DatabaseError extends DomainError {
  constructor(message: string) {
    super(`Database error: ${message}`);
  }
}

export class AIModelError extends DomainError {
  constructor(message: string) {
    super(`AI model error: ${message}`);
  }
}
```

---

## UI COMPONENTS (renderer/)

### Features

| Feature Module | Componenti | Servizi |
|----------------|------------|---------|
| `dip-browser` | `FileTreeComponent`, `FileNodeComponent` | `TreeService` |
| `metadata` | `MetadataViewerComponent`, `MetadataTableComponent` | `MetadataApiService` |
| `search` | `SearchFiltersComponent`, `FilterGroupComponent`, `SemanticSearchComponent` | `SearchApiService` |
| `integrity` | `IntegrityBadgeComponent`, `IntegrityDialogComponent` | `IntegrityApiService` |
| `file-preview` | `FilePreviewComponent` | `FileApiService` |

### Servizi API (Bridge verso IPC)

```typescript
// renderer/src/app/services/

@Injectable({ providedIn: 'root' })
export class DatabaseApiService {
  init(): Promise<any>;
  open(dipUUID: string): Promise<OpenDatabaseResult>;
  index(dipUUID: string, dipPath: string): Promise<IndexResult>;
  query<T>(sql: string, params?: any[]): Promise<T>;
  list(): Promise<string[]>;
  delete(dipUUID: string): Promise<{ success: boolean }>;
  export(): Promise<{ success: boolean }>;
  getInfo(): Promise<DatabaseInfo>;
}

@Injectable({ providedIn: 'root' })
export class SearchApiService {
  loadFilterKeys(): Promise<string[]>;
  searchDocuments(name: string, filters: SearchFilter[]): Promise<FileNode[]>;
  searchSemantic(query: string): Promise<SemanticSearchResult[]>;
}

@Injectable({ providedIn: 'root' })
export class MetadataApiService {
  getMetadata(fileId: number): Promise<Metadata[]>;
  getDocumentMetadata(documentId: number): Promise<Metadata[]>;
}

@Injectable({ providedIn: 'root' })
export class FileApiService {
  getPhysicalPath(fileId: number): Promise<string | undefined>;
  openFile(path: string): Promise<{ success: boolean }>;
  downloadFile(path: string): Promise<{ success: boolean; savedPath?: string }>;
  readFile(path: string): Promise<{ success: boolean; data: ArrayBuffer }>;
}

@Injectable({ providedIn: 'root' })
export class IntegrityApiService {
  verify(fileId: number): Promise<IntegrityCheckResult>;
  getStoredStatus(fileId: number): Promise<SavedIntegrityStatus | null>;
  saveResult(fileId: number, result: IntegrityCheckResult): Promise<void>;
}

@Injectable({ providedIn: 'root' })
export class AIApiService {
  init(): Promise<any>;
  search(query: string): Promise<SemanticSearchResult[]>;
  generateEmbedding(text: string): Promise<Float32Array>;
  getState(): Promise<{ initialized: boolean; indexedDocuments: number }>;
}
```