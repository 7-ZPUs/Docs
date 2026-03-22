import { AppError } from '../../shared/domain/app-error';
 
export interface IErrorHandler {
  handleError(err: unknown, context: string): AppError;
  isRecoverable(err: AppError): boolean;
}