<script lang="ts">
	import Component from "./Component.svelte";
	export let data: { [key: string]: any };

	const formatIndex = (text:any, index:number) => {
		return String(text).replace(/(?<!\\){i}/g, () => String(index)).replace(/\\({i})/g, "$1");
	};

	const formatIndexAll = (targetData:any, index:number) => {
		return {
			tag: targetData.tag,
			attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatIndex(v,index)])),
			text: formatIndex(targetData.text,index),
			child: targetData.child.map((child:any) => formatIndexAll(child,index))
		};
	};

	const formatVlaue = (text:any, value:any) => {
		return String(text).replace(/(?<!\\){(\d+)}/g, (m,k) => String(value[Number(k)])).replace(/\\({\d+})/g, "$1");
	};

	const formatVlaueAll = (targetData:any, value:any) => {
		return {
			tag: targetData.tag,
			attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatVlaue(v,value)])),
			text: formatVlaue(targetData.text,value),
			child: targetData.child.map((child:any) => formatVlaueAll(child,value))
		};
	};

	$: repeatCount = Number(data.attr.data) || 0;
	$: repeatIndexes = Array.from({ length: repeatCount }, (_, index) => index);
	$: repeatedChildren = repeatIndexes.map((index) => data.child.map((child:any) => formatIndexAll(child, index)));
</script>
{#if String(data.attr.disabled??"")!="true"}
	{#each repeatedChildren as children}
		{#each children as child}
			<Component rawData={child}/>
		{/each}
	{/each}
{/if}