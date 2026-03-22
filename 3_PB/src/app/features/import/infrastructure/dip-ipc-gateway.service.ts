import { Injectable } from '@angular/core';
import { ElectronContextBridge }          from '../../../core/adapters/electron-context-bridge';
import { ClasseDocumentaleDto, DipTreeNodeDto } from '../domain/dtos';
import { IDipChannel }                    from '../contracts/i-dip-channel';
 
const CH = {
  GET_CLASSES:   'dip:get-classes',
  LOAD_CHILDREN: 'dip:load-children',
  DOWNLOAD_FILE: 'dip:download-file',
} as const;
 
@Injectable({ providedIn: 'root' })
export class DipIpcGateway implements IDipChannel {
 
  constructor(private readonly ipc: ElectronContextBridge) {}
 
  getClasses(): Promise<ClasseDocumentaleDto[]> {
    return this.ipc.invoke<ClasseDocumentaleDto[]>(CH.GET_CLASSES);
  }
 
  loadChildren(nodeId: string): Promise<DipTreeNodeDto[]> {
    return this.ipc.invoke<DipTreeNodeDto[]>(CH.LOAD_CHILDREN, nodeId);
  }
 
  downloadFile(nodeId: string): Promise<Blob> {
    return this.ipc.invoke<Blob>(CH.DOWNLOAD_FILE, nodeId);
  }
}