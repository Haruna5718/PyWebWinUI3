<script lang="ts">
	import { resolveDesktopResource } from './desktop';

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
