<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
{#if String(data.attr.disabled??"")!="true"}
{@const condition = (data.attr.raw??$values[data.attr.value])}
    {#each (data.child.find((d)=>condition==d.attr.value) ?? data.child.find((d)=>!d.attr.value))?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}