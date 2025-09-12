<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span style="
    gap: {data.attr.gap ?? 'inherit'};
    align-items: {data.attr.aligin?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
">
    <slot />
</span>
<style lang="scss">
    span{
        flex-wrap: wrap;
        align-self: stretch;
        display: flex;
		flex-direction: row;
    }
</style>