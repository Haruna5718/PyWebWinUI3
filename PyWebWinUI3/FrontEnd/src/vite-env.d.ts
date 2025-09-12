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
    setValue: (target: string, value: any, sync?: boolean) => void;
    appName:string;
    appIcon:string;
    values: {
      [key: string]: any;
    }
  }
}