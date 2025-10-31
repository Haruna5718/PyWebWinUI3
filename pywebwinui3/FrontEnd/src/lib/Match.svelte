<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#each data.child.find((d)=>$values[data.attr.value]==d.attr.value)?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}
<style lang="scss">
</style>