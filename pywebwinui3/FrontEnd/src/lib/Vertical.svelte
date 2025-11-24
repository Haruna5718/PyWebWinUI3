<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span style="
    gap: {data.attr.gap ?? 'inherit'};
    width: {data.attr.width ?? 'auto'};
    align-items: {data.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
">
    <slot />
</span>
<style lang="scss">
    span{
        transition: none;
        align-self: stretch;
        display: flex;
		flex-direction: column;
    }
</style>