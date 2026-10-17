<script lang="ts">
	import { onMount } from 'svelte';

	import { getDesktopApi, resolveDesktopResource } from './desktop';

	export let data: { [key: string]: any };

	let resolvedSource = '';
	let resolveRequest = 0;
	let sourceValue: unknown;
	let payloadValue: unknown;
	let frame: HTMLIFrameElement;
	let hasAspect = false;
	let aspectPadding = '56.25%';
	let wrapperHeight: unknown = '400px';

	const postData = () => {
		if (!frame?.contentWindow || payloadValue === undefined) {
			return;
		}

		frame.contentWindow.postMessage(payloadValue, '*');
	};

	let relayQueue = Promise.resolve();
	const relayFrameMessage = (event: MessageEvent) => {
		const key = data.attr.relay;
		if (typeof key !== 'string' || !key || event.source !== frame?.contentWindow) {
			return;
		}

		try {
			if (event.origin !== new URL(resolvedSource).origin || event.data?.type !== key) {
				return;
			}
		} catch (_) {
			return;
		}

		const requestId = event.data.value?.requestId;
		relayQueue = relayQueue
			.catch(() => {})
			.then(async () => {
				const result = await (await getDesktopApi()).message(key, event.data.value);
				if (typeof requestId !== 'string' || !frame?.contentWindow) {
					return;
				}

				frame.contentWindow.postMessage(
					{ type: key, value: { requestId, result } },
					new URL(resolvedSource).origin,
				);
			});
	};

	const relayHostMessage = (event: CustomEvent<{ key?: string; value?: unknown }>) => {
		if (event.detail?.key !== data.attr.relay || !frame?.contentWindow || !resolvedSource) {
			return;
		}

		try {
			frame.contentWindow.postMessage(
				{ type: event.detail.key, value: event.detail.value },
				new URL(resolvedSource).origin,
			);
		} catch (_) {
		}
	};

	onMount(() => {
		window.addEventListener('message', relayFrameMessage);
		window.addEventListener('pywebwinui3-message', relayHostMessage as EventListener);
		return () => {
			window.removeEventListener('message', relayFrameMessage);
			window.removeEventListener('pywebwinui3-message', relayHostMessage as EventListener);
		};
	});

	$: {
		const source = data.attr.source;
		if (source !== sourceValue) {
			sourceValue = source;
			const requestId = ++resolveRequest;

			if (typeof source !== 'string' || !source) {
				resolvedSource = source == null ? '' : String(source);
			} else {
				void resolveDesktopResource(source).then((nextSource) => {
					if (requestId === resolveRequest) {
						resolvedSource = nextSource || source;
					}
				});
			}
		}
	}

	$: payloadValue = data.attr.data;

	$: {
		hasAspect = !!data.attr.aspect;
		const aspectValue = typeof data.attr.aspect === 'string' ? data.attr.aspect : '16 / 9';
		const aspectParts = aspectValue
			.split('/')
			.map((part: string) => Number(part.trim()))
			.filter((part: number) => Number.isFinite(part) && part > 0);
		aspectPadding = aspectParts.length === 2 ? `${(aspectParts[1] / aspectParts[0]) * 100}%` : '56.25%';
		wrapperHeight = hasAspect ? '0' : (data.attr.height ?? '400px');
	}

	$: if (resolvedSource) {
		payloadValue;
		postData();
	}
</script>

<div class:disabled={String(data.attr.disabled??"")=="true"} class:ratio={hasAspect} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {wrapperHeight};
	border-radius: {data.attr.round ?? 0};
	background-color: {data.attr.background ?? 'transparent'};
	--ratio-padding: {aspectPadding};
">
	<iframe bind:this={frame} src={resolvedSource} title="Webview" allow={data.attr.allow} on:load={postData}></iframe>
</div>
<style lang="scss">
	div{
		width: 100%;
		max-width: 100%;
		align-self: center;
		overflow: hidden;
		position: relative;
	}

	div.ratio{
		height: 0 !important;
		padding-top: var(--ratio-padding);
	}

	iframe{
		width: 100%;
		height: 100%;
		max-width: 100%;
		border: 0;
		display: block;
	}

	div.ratio iframe{
		position: absolute;
		inset: 0;
	}
</style>
