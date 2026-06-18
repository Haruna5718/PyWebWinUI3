/// <reference types="svelte" />
/// <reference types="vite/client" />
export {};

declare global {
	interface DesktopApi {
		init: () => Promise<Record<string, any>>;
		frontendReady: () => void;
		syncValue: (target: string, value: any) => void;
		syncValues: (patch: Record<string, any>) => void;
		resolveResource: (source: string) => Promise<string>;
		pin: (state: boolean) => void;
		startWindowDrag: () => void;
		toggleWindowMaximize: () => void;
		showWindowSystemMenu: () => void;
		minimize: () => void;
		destroy: () => void;
		openExternal: (url: string) => void;
	}

	interface Window {
		pywebview?: {
			api: {
				init: () => Promise<Record<string, any>> | Record<string, any>;
				frontendReady?: () => Promise<any> | any;
				syncValue: (target: string, value: any) => Promise<any> | any;
				syncValues?: (patch: Record<string, any>) => Promise<any> | any;
				resolveResource?: (source: string) => Promise<string> | string;
				pin?: (state: boolean) => Promise<any> | any;
				startWindowDrag?: () => Promise<any> | any;
				toggleWindowMaximize?: () => Promise<any> | any;
				showWindowSystemMenu?: () => Promise<any> | any;
				minimize?: () => Promise<any> | any;
				destroy?: () => Promise<any> | any;
				openExternal?: (url: string) => Promise<any> | any;
			};
		};
		desktop?: {
			api: DesktopApi;
		};
		syncValue: (target: string, value: any, sync?: boolean) => void;
		applyBackendPatch: (patch: Record<string, any>) => void;
	}
}
