/// <reference types="svelte" />
/// <reference types="vite/client" />
export {};

declare global {
	interface DesktopApi {
		init: () => Promise<Record<string, any>>;
		syncValue: (target: string, value: any) => void;
		syncValues: (patch: Record<string, any>) => void;
		resolveResource: (source: string) => Promise<string>;
		pin: (state: boolean) => void;
		minimize: () => void;
		destroy: () => void;
		frontendReady: () => void;
		startWindowDrag: () => void;
		startWindowResize: (edge: string) => void;
		toggleMaximize: () => void;
		openExternal: (url: string) => void;
	}

	interface Window {
		qt?: {
			webChannelTransport: unknown;
		};
		desktop?: {
			api: DesktopApi;
		};
		QWebChannel?: new (
			transport: unknown,
			callback: (channel: { objects: { backend: unknown } }) => void
		) => unknown;
		syncValue: (target: string, value: any, sync?: boolean) => void;
		applyBackendPatch: (patch: Record<string, any>) => void;
	}
}