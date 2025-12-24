<script lang="ts">
    export let data: { [key: string]: any };
</script>
<div style="
    gap: {data.attr.gap ?? 'inherit'};
    border-radius: {data.attr.round ?? '4px'};
    border-width: {data.attr.border ?? '1px'};
    margin: {data.attr.margin ?? 0};
    padding: {data.attr.padding ?? '16px'};
    background-color: {data.attr.background ?? 'var(--CardBackgroundFillColorDefaultBrush)'};
    align-items: {data.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
">
    <slot />
</div>
<style lang="scss">
    div{
        display: flex;
        align-items: center;
        flex-direction: column;
        align-self: stretch;

        border-color: var(--CardStrokeColorDefaultSolidBrush);
        border-style: solid;
    }
</style>