<script lang="ts">
    export let data: { [key: string]: any };
</script>
<img src={data.attr.source} alt={data.attr.source}>
<style lang="scss">
    img{
        display: flex;
        max-width: 100%;
        align-self: center;
    }
</style>