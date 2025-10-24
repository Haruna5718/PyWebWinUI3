<script lang="ts">
    export let data: { [key: string]: any };
</script>
<hr style="
    margin: {data.attr.margin??0};
    border-width: {data.attr.size??'1'};
    border-color: {data.attr.color??'var(--TextFillColorSecondaryBrush)'};
">
<style lang="scss">
    hr{
        border-style: solid;
        align-self: stretch;
        flex-grow: 1;
    }
</style>