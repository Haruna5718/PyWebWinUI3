<script lang="ts">
    export let data: { [key: string]: any };
</script>
<hr style={data.attr.style}>
<style lang="scss">
    hr{
        width: 100%;
        flex-grow: 1;
        border-color: #ffffff9f;
        margin: 10px 0px;
    }
</style>