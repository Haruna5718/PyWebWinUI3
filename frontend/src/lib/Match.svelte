<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#each (data.child.find((d:any)=>data.attr.data==d.attr.target) ?? data.child.find((d:any)=>!d.attr.target))?.child ?? [] as val}
        <Component rawData={val}/>
    {/each}
{/if}