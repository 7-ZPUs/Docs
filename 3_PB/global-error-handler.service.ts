import { Injectable } from '@angular/core';
import { AppError } from '../../shared/domain/app-error';
import { ErrorCategory, ErrorCode } from '../../shared/domain/app-error';
import { IErrorHandler } from '../contracts/i-error-handler';
 
@Injectable({ providedIn: 'root' })
export class GlobalErrorHandlerService implements IErrorHandler {
 
  handleError(err: unknown, context: string): AppError {
    if (err instanceof AppError) return err;
    const message = err instanceof Error ? err.message : 'Errore sconosciuto';
    return new AppError(
      ErrorCode.UNKNOWN,
      ErrorCategory.UNKNOWN,
      context,
      message,
      true,
      String(err),
    );
  }
 
  isRecoverable(err: AppError): boolean {
    return err.recoverable;
  }
}