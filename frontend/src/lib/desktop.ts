let desktopApiPromise: Promise<DesktopApi> | null = null;

const waitForDesktopApi = async (): Promise<DesktopApi> => {
	if (typeof window === 'undefined') {
		return {
			init: async () => ({}),
			frontendReady: () => {},
			syncValue: () => {},
			syncValues: () => {},
			resolveResource: async (source) => source,
			pin: () => {},
			startWindowDrag: () => {},
			toggleWindowMaximize: () => {},
			showWindowSystemMenu: () => {},
			minimize: () => {},
			destroy: () => {},
			openExternal: () => {},
		};
	}

	for (;;) {
		const api = window.desktop?.api ?? window.pywebview?.api;
		if (api?.init && api?.syncValue) {
			const wrapped: DesktopApi = {
				init: async () => await api.init(),
				frontendReady: () => {
					if (typeof api.frontendReady === 'function') {
						void api.frontendReady();
					}
				},
				syncValue: (target, value) => {
					void api.syncValue(target, value);
				},
				syncValues: (patch) => {
					if (typeof api.syncValues === 'function') {
						void api.syncValues(patch);
						return;
					}
					for (const [key, value] of Object.entries(patch ?? {})) {
						void api.syncValue(key, value);
					}
				},
				resolveResource: async (source) => {
					if (typeof api.resolveResource !== 'function') {
						return source;
					}
					return await api.resolveResource(source);
				},
				pin: (state) => {
					if (typeof api.pin === 'function') {
						void api.pin(state);
					}
				},
				startWindowDrag: () => {
					if (typeof api.startWindowDrag === 'function') {
						void api.startWindowDrag();
					}
				},
				toggleWindowMaximize: () => {
					if (typeof api.toggleWindowMaximize === 'function') {
						void api.toggleWindowMaximize();
					}
				},
				showWindowSystemMenu: () => {
					if (typeof api.showWindowSystemMenu === 'function') {
						void api.showWindowSystemMenu();
					}
				},
				minimize: () => {
					if (typeof api.minimize === 'function') {
						void api.minimize();
					}
				},
				destroy: () => {
					if (typeof api.destroy === 'function') {
						void api.destroy();
					}
				},
				openExternal: (url) => {
					if (typeof api.openExternal === 'function') {
						void api.openExternal(url);
						return;
					}
					window.open(url, '_blank', 'noopener,noreferrer');
				},
			};
			window.desktop = { api: wrapped };
			return wrapped;
		}

		await new Promise((resolve) => window.setTimeout(resolve, 50));
	}
};

export const getDesktopApi = () => {
	if (desktopApiPromise == null) {
		desktopApiPromise = waitForDesktopApi();
	}
	return desktopApiPromise;
};

export const queueDesktopSync = (target: string, value: any) => {
	void getDesktopApi().then((api) => {
		api.syncValue(target, value);
	});
};

export const resolveDesktopResource = async (source: string) => {
	const api = await getDesktopApi();
	return await api.resolveResource(source);
};
