<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
{#if !data.attr.disabled}
    {#each data.child.find((d)=>$values[data.attr.value]?"True":"False"==d.tag)?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}
<style lang="scss">
</style>