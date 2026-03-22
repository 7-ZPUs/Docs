import { Injectable, Signal } from '@angular/core';
import { AuditLogger }           from '../../../core/telemetry/audit-logger.service';
import { LiveAnnouncerService }  from '../../../core/telemetry/live-announcer.service';
import { PerformanceMonitor }    from '../../../core/telemetry/performance-monitor.service';
import { ErrorCategory }         from '../../../shared/domain/app-error';
import { IExportFacade }         from '../contracts/i-export-facade';
import { ExportIpcGateway }      from '../infrastructure/export-ipc-gateway.service';
import { ExportState }           from '../domain/export.state';
import { ExportError, ExportItemError, ExportResult } from '../domain/models';
import { ExportErrorCode, ExportPhase, OutputContext } from '../domain/enums';
import { DipTreeNode } from '../../import/domain/models';
 
const PRINTABLE_FORMATS = ['pdf', 'png', 'jpg', 'jpeg', 'tiff'];
 
@Injectable({ providedIn: 'root' })
export class ExportFacade implements IExportFacade {
 
  constructor(
    private readonly exportState:   ExportState,
    private readonly ipcGateway:    ExportIpcGateway,
    private readonly auditLogger:   AuditLogger,
    private readonly perfMonitor:   PerformanceMonitor,
    private readonly liveAnnouncer: LiveAnnouncerService,
  ) {}
 
  // Segnali esposti ai componenti
  get phase():         Signal<ExportPhase>         { return this.exportState.phase; }
  get outputContext(): Signal<OutputContext | null> { return this.exportState.outputContext; }
  get result():        Signal<ExportResult | null> { return this.exportState.result; }
  get progress():      Signal<number>              { return this.exportState.progress; }
  get error():         Signal<ExportError | null>  { return this.exportState.error; }
  get loading():       Signal<boolean>             { return this.exportState.loading; }
 
  // ------------------------------------------------------------------
  // UC-19 — salvataggio singolo documento
  // ------------------------------------------------------------------
  async exportDocument(node: DipTreeNode): Promise<void> {
    this.exportState.setProcessing(OutputContext.SINGLE_EXPORT);
 
    await this.perfMonitor.measure('exportDocument', async () => {
      try {
        const dialog = await this.ipcGateway.openSaveDialog(node.label);
        if (dialog.canceled || !dialog.filePath) { this.exportState.reset(); return; }
 
        const res = await this.ipcGateway.exportDocument(node.id, dialog.filePath);
 
        if (!res.success) throw new Error(res.errorMessage ?? 'Export fallito');
 
        const result = new ExportResult(OutputContext.SINGLE_EXPORT, 1, 1, 0, dialog.filePath);
        this.exportState.setSuccess(result);
        this.liveAnnouncer.announce('Documento salvato con successo');
        this.audit('exportDocument', [node.id], dialog.filePath);
 
      } catch (err) {
        this.handleError(ExportErrorCode.EXPORT_WRITE_FAILED, err, 'exportDocument');
      }
    });
  }
 
  // ------------------------------------------------------------------
  // UC-20 — salvataggio multiplo documenti
  // ------------------------------------------------------------------
  async exportDocuments(nodes: DipTreeNode[]): Promise<void> {
    this.exportState.setProcessing(OutputContext.MULTI_EXPORT);
 
    await this.perfMonitor.measure('exportDocuments', async () => {
      try {
        const dialog = await this.ipcGateway.openSaveDialog();
        if (dialog.canceled || !dialog.filePath) { this.exportState.reset(); return; }
 
        const errors: ExportItemError[] = [];
        let success = 0;
 
        for (let i = 0; i < nodes.length; i++) {
          const res = await this.ipcGateway.exportDocument(nodes[i].id, dialog.filePath);
          if (res.success) { success++; }
          else { errors.push({ nodeId: nodes[i].id, nodeName: nodes[i].label, reason: res.errorMessage ?? 'Errore' }); }
          this.exportState.setProgress(((i + 1) / nodes.length) * 100);
        }
 
        const result = new ExportResult(OutputContext.MULTI_EXPORT, nodes.length, success, errors.length, dialog.filePath, errors);
        this.exportState.setSuccess(result);
        this.liveAnnouncer.announce(`${success} documenti salvati su ${nodes.length}`);
        this.audit('exportDocuments', nodes.map(n => n.id), dialog.filePath);
 
      } catch (err) {
        this.handleError(ExportErrorCode.EXPORT_WRITE_FAILED, err, 'exportDocuments');
      }
    });
  }
 
  // ------------------------------------------------------------------
  // UC-34 — esporta report verifica in PDF
  // UC-37 — errore generazione PDF
  // ------------------------------------------------------------------
  async exportReportPdf(reportId: string): Promise<void> {
    this.exportState.setProcessing(OutputContext.REPORT_PDF);
 
    await this.perfMonitor.measure('exportReportPdf', async () => {
      try {
        const res = await this.ipcGateway.exportReportPdf(reportId);
        if (!res.success || !res.blob) throw new Error(res.errorMessage ?? 'Generazione PDF fallita');
 
        const result = new ExportResult(OutputContext.REPORT_PDF, 1, 1, 0, reportId);
        this.exportState.setSuccess(result);
        this.liveAnnouncer.announce('Report PDF esportato');
        this.audit('exportReportPdf', [reportId]);
 
      } catch (err) {
        // UC-37
        this.handleError(ExportErrorCode.EXPORT_PDF_FAILED, err, 'exportReportPdf');
      }
    });
  }
 
  // ------------------------------------------------------------------
  // UC-22 — stampa singolo documento
  // UC-25 — stampa non disponibile (formato non supportato)
  // ------------------------------------------------------------------
  async printDocument(node: DipTreeNode): Promise<void> {
    if (!this.checkPrintable(node)) {
      // UC-25
      const err = new ExportError(ExportErrorCode.PRINT_UNAVAILABLE, ErrorCategory.VALIDATION, 'printDocument', `Formato non supportato per la stampa: ${node.label}`, false);
      this.exportState.setUnavailable(err);
      return;
    }
 
    this.exportState.setProcessing(OutputContext.SINGLE_PRINT);
 
    await this.perfMonitor.measure('printDocument', async () => {
      try {
        const res = await this.ipcGateway.printDocument(node.id);
        if (!res.success) throw new Error(res.errorMessage ?? 'Stampa fallita');
 
        const result = new ExportResult(OutputContext.SINGLE_PRINT, 1, 1, 0, '');
        this.exportState.setSuccess(result);
        this.liveAnnouncer.announce('Documento inviato alla stampante');
        this.audit('printDocument', [node.id]);
 
      } catch (err) {
        // UC-24
        this.handleError(ExportErrorCode.PRINT_FAILED, err, 'printDocument');
      }
    });
  }
 
  // ------------------------------------------------------------------
  // UC-23 — stampa insieme documenti
  // ------------------------------------------------------------------
  async printDocuments(nodes: DipTreeNode[]): Promise<void> {
    const printable = nodes.filter(n => this.checkPrintable(n));
 
    if (printable.length === 0) {
      const err = new ExportError(ExportErrorCode.PRINT_UNAVAILABLE, ErrorCategory.VALIDATION, 'printDocuments', 'Nessun documento nel formato supportato per la stampa', false);
      this.exportState.setUnavailable(err);
      return;
    }
 
    this.exportState.setProcessing(OutputContext.MULTI_PRINT);
 
    await this.perfMonitor.measure('printDocuments', async () => {
      try {
        const errors: ExportItemError[] = [];
        let success = 0;
 
        for (let i = 0; i < printable.length; i++) {
          const res = await this.ipcGateway.printDocument(printable[i].id);
          if (res.success) { success++; }
          else { errors.push({ nodeId: printable[i].id, nodeName: printable[i].label, reason: res.errorMessage ?? 'Errore stampa' }); }
          this.exportState.setProgress(((i + 1) / printable.length) * 100);
        }
 
        const result = new ExportResult(OutputContext.MULTI_PRINT, printable.length, success, errors.length, '', errors);
        this.exportState.setSuccess(result);
        this.liveAnnouncer.announce(`${success} documenti inviati alla stampante`);
        this.audit('printDocuments', printable.map(n => n.id));
 
      } catch (err) {
        this.handleError(ExportErrorCode.PRINT_FAILED, err, 'printDocuments');
      }
    });
  }
 
  reset(): void {
    this.exportState.reset();
  }
 
  // ------------------------------------------------------------------
  // UC-25 — controlla se il formato è stampabile
  // ------------------------------------------------------------------
  private checkPrintable(node: DipTreeNode): boolean {
    return PRINTABLE_FORMATS.some(ext => node.label.toLowerCase().endsWith(`.${ext}`));
  }
 
  private handleError(code: ExportErrorCode, err: unknown, context: string): void {
    const message = err instanceof Error ? err.message : 'Errore sconosciuto';
    const exportError = new ExportError(code, ErrorCategory.IPC, context, message, true);
    this.exportState.setError(exportError);
    this.auditLogger.log({ action: `${context}:error`, context: 'ExportFacade', timestamp: new Date(), payload: { error: message } });
  }
 
  private audit(action: string, nodeIds: string[], destPath?: string): void {
    this.auditLogger.log({ action, context: 'ExportFacade', timestamp: new Date(), payload: { nodeIds, destPath } });
  }
}