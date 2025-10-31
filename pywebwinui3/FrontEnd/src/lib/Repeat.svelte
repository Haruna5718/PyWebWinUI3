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
            child: targetData.child.map((child) => formatIndexAll(child,index))
        };
    };

    const formatVlaue = (text,value) => {
        return text.replace(/(?<!\\){(\d+)}/g, (m,k) => value[Number(k)]).replace(/\\({\d+})/g, "$1");
    };

    const formatVlaueAll = (targetData,value) => {
        return {
            tag: targetData.tag,
            attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatVlaue(v,value)])),
            text: formatVlaue(targetData.text,value),
            child: targetData.child.map((child) => formatVlaueAll(child,value))
        };
    };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#if data.attr.data && ($values[data.attr.data]??[]).length}
        {#each $values[data.attr.data]??[] as indexValue}
            {#each data.child as val}
                <Component rawData={formatVlaueAll(val,indexValue)}/>
            {/each}
        {/each}
    {:else}
        {#each new Array(Number($values[data.attr.value])||0) as _,index}
            {#each data.child as val}
                <Component rawData={formatIndexAll(val,index)}/>
            {/each}
        {/each}
    {/if}
{/if}
<style lang="scss">
</style>