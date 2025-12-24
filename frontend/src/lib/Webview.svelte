<script lang="ts">
    export let data: { [key: string]: any };
</script>
<iframe src={data.attr.source} title="Webview" class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
"></iframe>
<style lang="scss">
    iframe{
        width: 100%;
        height: 400px;
        max-width: 100%;
        border: 0;
        align-self: center;
    }
</style>