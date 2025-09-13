<script lang="ts">
    export let data: { [key: string]: any };
</script>

{#if data.attr.url}
    <a class="text {data.attr.type}" target="_blank" href={data.attr.url} style="
        margin: {data.attr.margin ?? 0}
    ">
        {data.text}
</a>
{:else}
    <span class="text {data.attr.type}" style="
        margin: {data.attr.margin ?? 0}
    ">
        {data.text}
    </span>
{/if}
<style lang="scss">
    .text{
        word-wrap: break-word;
		overflow-wrap: anywhere;
        display: flex;
        font-size: 16px;
    }
    a{
        text-decoration: none;
        color: var(--AccentFillColorSecondaryBrush) !important;
        outline: none ;
    }
    .description{
        color: var(--TextFillColorTertiaryBrush);
        font-size: 12px;
    }
    .title{
        font-size: 24px;
    }
</style>