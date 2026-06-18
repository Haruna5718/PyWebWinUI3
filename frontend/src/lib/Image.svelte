<script lang="ts">
	import { resolveDesktopResource } from './desktop';

	export let data: { [key: string]: any };

	let resolvedSource = '';
	let resolveRequest = 0;
	let sourceValue: unknown;

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
</script>
<img src={resolvedSource} alt="" class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
	border-radius: {data.attr.round ?? 0};
	background-color: {data.attr.background ?? 'transparent'};
	object-fit: {data.attr.fit ?? 'contain'};
">
<style lang="scss">
	img{
		display: flex;
		max-width: 100%;
		align-self: center;
	}
</style>
