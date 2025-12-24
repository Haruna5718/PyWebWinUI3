<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {@const condition = (data.attr.raw??data.attr.data)?"True":"False"}
    {#each data.child.find((d:any)=>condition==d.tag)?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}