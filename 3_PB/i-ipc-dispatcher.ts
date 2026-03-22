export interface IIpcDispatcher {
  invoke<T>(channel: string, ...args: unknown[]): Promise<T>;
  on<T>(channel: string, handler: (data: T) => void): void;
}
 
export const IPC_DISPATCHER_TOKEN = 'IPC_DISPATCHER_TOKEN';
 