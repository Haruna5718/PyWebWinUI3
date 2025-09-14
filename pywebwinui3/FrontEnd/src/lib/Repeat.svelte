<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    export const formatIndex = (text,index) => {
        return text.replace(/(?<!\\){i}/g, () => index).replace(/\\({i})/g, "$1");
    };
</script>
{#if !data.attr.disabled}
    {#each new Array(Number($values[data.attr.value])||0) as _,index}
        {#each data.child as val}
            {@const formatData = {
                tag: val.tag,
                attr: Object.fromEntries(Object.entries(val.attr).map(([k, v]) => [k, formatIndex(v,index)])),
                text: formatIndex(val.text,index),
                child: val.child
            }}
            <Component {formatData}/>
        {/each}
    {/each}
{/if}
<style lang="scss">
</style>