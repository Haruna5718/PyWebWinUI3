<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
	type ComponentNode = Record<string, any>;
	const ifBranchCache = new WeakMap<ComponentNode[], Record<string, ComponentNode[]>>();

	const getIfBranches = (children: ComponentNode[]) => {
		let cached = ifBranchCache.get(children);
		if (cached) {
			return cached;
		}

		cached = {};
		for (const child of children) {
			cached[child.tag] = child.child ?? [];
		}
		ifBranchCache.set(children, cached);
		return cached;
	};

	$: condition = (data.attr.raw ?? data.attr.data) ? "True" : "False";
	$: branchChildren = getIfBranches(data.child ?? [])[condition] ?? [];
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#each branchChildren as val}
        <Component rawData={val}/>
    {/each}
{/if}
