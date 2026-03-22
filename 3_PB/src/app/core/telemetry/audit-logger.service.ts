import { Injectable } from '@angular/core';
import { AuditEvent } from '../../shared/domain/audit-event';
 
@Injectable({ providedIn: 'root' })
export class AuditLogger {
  log(event: AuditEvent): void {
    // TODO: inviare via IPC al Main Process per persistenza AGID-compliant
    console.info('[AUDIT]', JSON.stringify(event));
  }
}