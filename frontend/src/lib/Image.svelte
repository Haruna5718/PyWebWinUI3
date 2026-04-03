<script lang="ts">
	import { onMount } from 'svelte';
	import { getDesktopResourceContextVersion, onDesktopResourceContextChange, resolveDesktopResource } from './desktop';

	export let data: { [key: string]: any };

	let resolvedSource = '';
	let resolveRequest = 0;
	let sourceValue: unknown;
	let resourceContextVersion = getDesktopResourceContextVersion();
	let resolvedContextVersion = -1;

	onMount(() => onDesktopResourceContextChange((version) => {
		resourceContextVersion = version;
	}));

	$: {
		const source = data.attr.source;
		if (source !== sourceValue || resolvedContextVersion !== resourceContextVersion) {
			sourceValue = source;
			resolvedContextVersion = resourceContextVersion;
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
</script>
<img src={resolvedSource} alt="" class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
">
<style lang="scss">
	img{
		display: flex;
		max-width: 100%;
		align-self: center;
	}
</style>
