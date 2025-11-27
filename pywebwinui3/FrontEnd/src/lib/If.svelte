<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {@const condition = (data.attr.raw??$values[data.attr.value])?"True":"False"}
    {#each data.child.find((d)=>condition==d.tag)?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}