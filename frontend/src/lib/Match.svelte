<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
	type ComponentNode = Record<string, any>;
	type MatchLookup = { targetMap: Map<string, ComponentNode[]>; fallback: ComponentNode[] };
	const matchBranchCache = new WeakMap<ComponentNode[], MatchLookup>();

	const getMatchLookup = (children: ComponentNode[]) => {
		let cached = matchBranchCache.get(children);
		if (cached) {
			return cached;
		}

		const targetMap = new Map<string, ComponentNode[]>();
		let fallback: ComponentNode[] = [];
		for (const child of children) {
			const target = child.attr?.target;
			if (target) {
				targetMap.set(String(target), child.child ?? []);
				continue;
			}
			fallback = child.child ?? [];
		}

		cached = { targetMap, fallback };
		matchBranchCache.set(children, cached);
		return cached;
	};

	$: lookup = getMatchLookup(data.child ?? []);
	$: branchChildren = lookup.targetMap.get(String(data.attr.data)) ?? lookup.fallback;
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#each branchChildren as val}
        <Component rawData={val}/>
    {/each}
{/if}
