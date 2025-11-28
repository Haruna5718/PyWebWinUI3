<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span style="
    gap: {data.attr.gap ?? 'inherit'};
    padding: {data.attr.padding ?? 0};
    margin: {data.attr.margin ?? 0};
    height: {data.attr.width ?? 'auto'};
    align-items: {data.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
">
    <slot />
</span>
<style lang="scss">
    span{
        transition: none;
        flex-wrap: wrap;
        align-self: stretch;
        display: flex;
		flex-direction: row;
    }
</style>