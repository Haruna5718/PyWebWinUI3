<script lang="ts">
	import { resolveDesktopResource } from './desktop';

	export let data: { [key: string]: any };

	let resolvedSource = '';
	let resolveRequest = 0;
	let sourceValue: unknown;
	let payloadValue: unknown;
	let frame: HTMLIFrameElement;

	const postData = () => {
		if (!frame?.contentWindow || payloadValue === undefined) {
			return;
		}

		frame.contentWindow.postMessage(payloadValue, '*');
	};

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

	$: if (resolvedSource) {
		payloadValue;
		postData();
	}
</script>
<iframe bind:this={frame} src={resolvedSource} title="Webview" class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
" on:load={postData}></iframe>
<style lang="scss">
	iframe{
		width: 100%;
		height: 400px;
		max-width: 100%;
		border: 0;
		align-self: center;
	}
</style>
