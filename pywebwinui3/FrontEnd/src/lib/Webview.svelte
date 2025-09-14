<script lang="ts">
    export let data: { [key: string]: any };
</script>
<iframe src={data.attr.source} title="Webview" class:disabled={Boolean(data.attr.disabled)} style="
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
"/>
<style lang="scss">
    iframe{
        width: 100%;
        height: 400px;
        max-width: 100%;
        border: 0;
        align-self: center;
    }
</style>