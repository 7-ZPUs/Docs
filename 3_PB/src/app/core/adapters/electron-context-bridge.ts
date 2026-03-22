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
    return window.electronAPI.invoke<T>(channel, ...args);
  }
 
  on<T>(channel: string, handler: (data: T) => void): void {
    window.electronAPI.on<T>(channel, handler);
  }
}