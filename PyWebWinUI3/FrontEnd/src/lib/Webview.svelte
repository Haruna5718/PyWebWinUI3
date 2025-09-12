<script lang="ts">
    export let data: { [key: string]: any };
</script>
<iframe src={data.attr.source} title="Webview"/>
<style lang="scss">
    iframe{
        border: 0;
        align-self: center;
    }
</style>