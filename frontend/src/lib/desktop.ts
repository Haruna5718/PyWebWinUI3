export type DesktopState = Record<string, any>;

type RawDesktopBackend = {
	init: (callback: (state: DesktopState) => void) => void;
	syncValue: (target: string, value: any) => void;
	syncValues: (patch: DesktopState) => void;
	resolveResource: (source: string, callback: (resolved: string) => void) => void;
	pin: (state: boolean) => void;
	minimize: () => void;
	destroy: () => void;
	frontendReady: () => void;
	startWindowDrag: () => void;
	startWindowResize: (edge: string) => void;
	toggleMaximize: () => void;
	openExternal: (url: string) => void;
};

export type DesktopApi = {
	init: () => Promise<DesktopState>;
	syncValue: (target: string, value: any) => void;
	syncValues: (patch: DesktopState) => void;
	resolveResource: (source: string) => Promise<string>;
	pin: (state: boolean) => void;
	minimize: () => void;
	destroy: () => void;
	frontendReady: () => void;
	startWindowDrag: () => void;
	startWindowResize: (edge: string) => void;
	toggleMaximize: () => void;
	openExternal: (url: string) => void;
};

const mockApi: DesktopApi = {
	init: async () => ({}),
	syncValue: () => {},
	syncValues: () => {},
	resolveResource: async (source: string) => source,
	pin: () => {},
	minimize: () => {},
	destroy: () => {},
	frontendReady: () => {},
	startWindowDrag: () => {},
	startWindowResize: () => {},
	toggleMaximize: () => {},
	openExternal: (url: string) => {
		if (url) {
			window.open(url, '_blank');
		}
	}
};

let desktopApiPromise: Promise<DesktopApi> | null = null;
let pendingSyncPatch: DesktopState = {};
let pendingSyncFrame = 0;
let dragBindingsInstalled = false;
const resourceResolutionCache = new Map<string, Promise<string>>();
const EXTERNAL_RESOURCE_PATTERN = /^(?:[a-z][a-z0-9+.-]*:|\/\/)/i;
const WINDOWS_ABSOLUTE_PATH_PATTERN = /^[a-z]:[\\/]/i;

const INTERACTIVE_SELECTOR = 'button, input, textarea, select, option, a, label, iframe, [data-no-drag], [contenteditable="true"]';

const wrapBackend = (backend: RawDesktopBackend): DesktopApi => ({
	init: () => new Promise((resolve) => backend.init(resolve)),
	syncValue: (target: string, value: any) => backend.syncValue(target, value),
	syncValues: (patch: DesktopState) => backend.syncValues(patch),
	resolveResource: (source: string) => new Promise((resolve) => backend.resolveResource(source, resolve)),
	pin: (state: boolean) => backend.pin(state),
	minimize: () => backend.minimize(),
	destroy: () => backend.destroy(),
	frontendReady: () => backend.frontendReady(),
	startWindowDrag: () => backend.startWindowDrag(),
	startWindowResize: (edge: string) => backend.startWindowResize(edge),
	toggleMaximize: () => backend.toggleMaximize(),
	openExternal: (url: string) => backend.openExternal(url)
});

const loadQtWebChannel = async () => {
	if (typeof window === 'undefined' || typeof window.QWebChannel !== 'undefined') {
		return;
	}

	await new Promise<void>((resolve, reject) => {
		const script = document.createElement('script');
		script.src = 'qrc:///qtwebchannel/qwebchannel.js';
		script.onload = () => resolve();
		script.onerror = () => reject(new Error('Failed to load Qt WebChannel.'));
		document.head.append(script);
	});
};

export const getDesktopApi = () => {
	if (typeof window === 'undefined') {
		return Promise.resolve(mockApi);
	}

	if (window.desktop?.api) {
		return Promise.resolve(window.desktop.api);
	}

	if (!desktopApiPromise) {
		desktopApiPromise = (async () => {
			const transport = window.qt?.webChannelTransport;
			if (!transport) {
				window.desktop = { api: mockApi };
				return mockApi;
			}

			try {
				await loadQtWebChannel();
				const api = await new Promise<DesktopApi>((resolve, reject) => {
					if (typeof window.QWebChannel === 'undefined') {
						reject(new Error('QWebChannel is not available.'));
						return;
					}

					new window.QWebChannel(transport, (channel) => {
						const backend = channel.objects.backend as RawDesktopBackend | undefined;
						if (!backend) {
							resolve(mockApi);
							return;
						}

						resolve(wrapBackend(backend));
					});
				});

				window.desktop = { api };
				return api;
			} catch (error) {
				console.error(error);
				window.desktop = { api: mockApi };
				return mockApi;
			}
		})();
	}

	return desktopApiPromise;
};

export const queueDesktopSync = (target: string, value: any) => {
	if (!target) {
		return;
	}

	pendingSyncPatch[target] = value;
	if (pendingSyncFrame) {
		return;
	}

	pendingSyncFrame = window.requestAnimationFrame(() => {
		const patch = pendingSyncPatch;
		pendingSyncPatch = {};
		pendingSyncFrame = 0;

		void getDesktopApi().then((api) => {
			api.syncValues(patch);
		});
	});
};

export const resolveDesktopResource = (source: unknown) => {
	if (typeof source !== 'string' || !source) {
		return Promise.resolve(source == null ? '' : String(source));
	}

	if (EXTERNAL_RESOURCE_PATTERN.test(source) || WINDOWS_ABSOLUTE_PATH_PATTERN.test(source)) {
		return Promise.resolve(source);
	}

	const cached = resourceResolutionCache.get(source);
	if (cached) {
		return cached;
	}

	const resolution = getDesktopApi()
		.then((api) => api.resolveResource(source))
		.then((resolved) => resolved || source)
		.catch(() => source);

	resourceResolutionCache.set(source, resolution);
	return resolution;
};

export const installDesktopWindowBindings = () => {
	if (typeof window === 'undefined' || dragBindingsInstalled) {
		return () => {};
	}

	const onMouseDown = (event: MouseEvent) => {
		if (event.button !== 0 || !(event.target instanceof Element)) {
			return;
		}

		const region = event.target.closest('.pywebview-drag-region');
		if (!region) {
			return;
		}

		const interactive = event.target.closest(INTERACTIVE_SELECTOR);
		if (interactive && interactive !== region) {
			return;
		}

		event.preventDefault();
		void getDesktopApi().then((api) => api.startWindowDrag());
	};

	const onDoubleClick = (event: MouseEvent) => {
		if (!(event.target instanceof Element)) {
			return;
		}

		const region = event.target.closest('.pywebview-drag-region.title');
		if (!region) {
			return;
		}

		const interactive = event.target.closest(INTERACTIVE_SELECTOR);
		if (interactive && interactive !== region) {
			return;
		}

		event.preventDefault();
		void getDesktopApi().then((api) => api.toggleMaximize());
	};

	document.addEventListener('mousedown', onMouseDown);
	document.addEventListener('dblclick', onDoubleClick);
	dragBindingsInstalled = true;

	return () => {
		document.removeEventListener('mousedown', onMouseDown);
		document.removeEventListener('dblclick', onDoubleClick);
		dragBindingsInstalled = false;
	};
};

export const openExternal = (url: string, target = '_blank') => {
	if (!url) {
		return;
	}

	void getDesktopApi().then((api) => {
		if (window.qt?.webChannelTransport) {
			api.openExternal(url);
			return;
		}

		window.open(url, target);
	});
};
