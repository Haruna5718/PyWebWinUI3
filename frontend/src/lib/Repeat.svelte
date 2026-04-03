<script lang="ts">
	import Component from "./Component.svelte";
	export let data: { [key: string]: any };
	type ComponentNode = Record<string, any>;
	const repeatNodeCache = new WeakMap<ComponentNode, Map<number, ComponentNode>>();
	const repeatChildrenCache = new WeakMap<ComponentNode[], Map<number, ComponentNode[][]>>();

	const formatIndex = (text:any, index:number) => {
		return String(text).replace(/(?<!\\){i}/g, () => String(index)).replace(/\\({i})/g, "$1");
	};

	const formatIndexAll = (targetData: ComponentNode, index: number): ComponentNode => {
		let cache = repeatNodeCache.get(targetData);
		if (!cache) {
			cache = new Map();
			repeatNodeCache.set(targetData, cache);
		}

		const cached = cache.get(index);
		if (cached) {
			return cached;
		}

		const formatted = {
			tag: targetData.tag,
			attr: Object.fromEntries(Object.entries(targetData.attr ?? {}).map(([k, v]) => [k, formatIndex(v, index)])),
			text: formatIndex(targetData.text, index),
			child: (targetData.child ?? []).map((child: ComponentNode) => formatIndexAll(child, index))
		};
		cache.set(index, formatted);
		return formatted;
	};

	const buildRepeatedChildren = (children: ComponentNode[], count: number) => {
		let cache = repeatChildrenCache.get(children);
		if (!cache) {
			cache = new Map();
			repeatChildrenCache.set(children, cache);
		}

		const cached = cache.get(count);
		if (cached) {
			return cached;
		}

		const repeated = Array.from({ length: count }, (_, index) =>
			children.map((child: ComponentNode) => formatIndexAll(child, index))
		);
		cache.set(count, repeated);
		return repeated;
	};

	$: repeatCount = Number(data.attr.data) || 0;
	$: repeatedChildren = buildRepeatedChildren(data.child ?? [], repeatCount);
</script>
{#if String(data.attr.disabled??"")!="true"}
	{#each repeatedChildren as children}
		{#each children as child}
			<Component rawData={child}/>
		{/each}
	{/each}
{/if}
