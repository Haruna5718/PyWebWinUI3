<script lang="ts">
    import Component from "./Component.svelte";
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    let target;
    $:{
        target = data.child.find((d)=>$values[data.attr.value]?"True":"False"==d.tag)?.child ?? []
    }
</script>
{#each target as val}
    <Component formatData={val}/>
{/each}
<style lang="scss">
</style>