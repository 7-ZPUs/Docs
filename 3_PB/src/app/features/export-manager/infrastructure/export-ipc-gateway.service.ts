import { Injectable } from '@angular/core';
import { ElectronContextBridge }    from '../../../core/adapters/electron-context-bridge';
import { IExportChannel }           from '../contracts/i-export-channel';
import { ExportPdfResponseDto, ExportResponseDto, SaveDialogResponseDto } from '../domain/dtos';
 
const CH = {
  EXPORT_DOC:      'export:document',       // UC-19
  EXPORT_DOCS:     'export:documents',      // UC-20
  EXPORT_PDF:      'export:report-pdf',     // UC-34
  PRINT_DOC:       'export:print-document', // UC-22
  PRINT_DOCS:      'export:print-documents',// UC-23
  SAVE_DIALOG:     'export:save-dialog',
} as const;
 
@Injectable({ providedIn: 'root' })
export class ExportIpcGateway implements IExportChannel {
 
  constructor(private readonly ipc: ElectronContextBridge) {}
 
  /** UC-19 */
  exportDocument(nodeId: string, destPath: string): Promise<ExportResponseDto> {
    return this.ipc.invoke<ExportResponseDto>(CH.EXPORT_DOC, nodeId, destPath);
  }
 
  /** UC-20 */
  exportDocuments(nodeIds: string[], destPath: string): Promise<ExportResponseDto> {
    return this.ipc.invoke<ExportResponseDto>(CH.EXPORT_DOCS, nodeIds, destPath);
  }
 
  /** UC-34 */
  exportReportPdf(reportId: string): Promise<ExportPdfResponseDto> {
    return this.ipc.invoke<ExportPdfResponseDto>(CH.EXPORT_PDF, reportId);
  }
 
  /** UC-22 */
  printDocument(nodeId: string): Promise<ExportResponseDto> {
    return this.ipc.invoke<ExportResponseDto>(CH.PRINT_DOC, nodeId);
  }
 
  /** UC-23 */
  printDocuments(nodeIds: string[]): Promise<ExportResponseDto> {
    return this.ipc.invoke<ExportResponseDto>(CH.PRINT_DOCS, nodeIds);
  }
 
  /** Apre dialog salvataggio OS */
  openSaveDialog(defaultName?: string): Promise<SaveDialogResponseDto> {
    return this.ipc.invoke<SaveDialogResponseDto>(CH.SAVE_DIALOG, defaultName);
  }
}