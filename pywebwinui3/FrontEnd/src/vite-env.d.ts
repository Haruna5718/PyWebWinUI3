/// <reference types="svelte" />
/// <reference types="vite/client" />
export {};

declare global {
  interface Window {
    pywebview: {
      api: {
        [key: string]: (...args: any[]) => any;
      };
    };
    syncValue: (target: string, value: any, sync?: boolean) => void;
  }
}