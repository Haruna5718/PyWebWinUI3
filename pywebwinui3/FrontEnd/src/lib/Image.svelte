<script lang="ts">
    export let data: { [key: string]: any };
</script>
<img src="{data.attr.source}" alt="" class:disabled={String(data.attr.disabled??"")=="true"} style="
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