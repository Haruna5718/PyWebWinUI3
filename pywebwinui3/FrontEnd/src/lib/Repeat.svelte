<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    const formatIndex = (text,index) => {
        return text.replace(/(?<!\\){i}/g, () => index).replace(/\\({i})/g, "$1");
    };

    const formatIndexAll = (targetData,index) => {
        return {
            tag: targetData.tag,
            attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatIndex(v,index)])),
            text: formatIndex(targetData.text,index),
            child: targetData.child.map((child,index) => formatIndexAll(child,index))
        };
    };
</script>
{#if !data.attr.disabled}
    {#each new Array(Number($values[data.attr.value])||0) as _,index}
        {#each data.child as val}
            <Component rawData={formatIndexAll(val,index)}/>
        {/each}
    {/each}
{/if}
<style lang="scss">
</style>