<script lang="ts">
    export let data: { [key: string]: any };
</script>
<img src={data.attr.source} alt={data.attr.source} class:disabled={Boolean(data.attr.disabled)} style="
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
">
<style lang="scss">
    img{
        display: flex;
        max-width: 100%;
        align-self: center;
    }
</style>