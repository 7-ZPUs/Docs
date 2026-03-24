import { Injectable } from '@angular/core';
import { IIpcDispatcher } from '../contracts/i-ipc-dispatcher';
 
declare global {
  interface Window {
    electronAPI: {
      invoke: <T>(channel: string, ...args: unknown[]) => Promise<T>;
      on:     <T>(channel: string, handler: (data: T) => void) => void;
    };
  }
}
 
@Injectable({ providedIn: 'root' })
export class ElectronContextBridge implements IIpcDispatcher {
 
  invoke<T>(channel: string, ...args: unknown[]): Promise<T> {
    return (globalThis as unknown as Window).electronAPI.invoke<T>(channel, ...args);
  }
 
  on<T>(channel: string, handler: (data: T) => void): void {
    (globalThis as unknown as Window).electronAPI.on<T>(channel, handler);
  }
}