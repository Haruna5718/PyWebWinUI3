<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span style={data.attr.style}>
    <slot />
</span>
<style lang="scss">
    span{
        flex-grow: 1;
    }
</style>