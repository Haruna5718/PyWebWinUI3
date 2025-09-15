<script lang="ts">
    export let data: { [key: string]: any };
</script>

{#if data.attr.url}
    <a class="text {data.attr.type}" class:disabled={Boolean(data.attr.disabled)} target="_blank" href={data.attr.url} style="
        margin: {data.attr.margin ?? 0};
        {data.attr.color?`color: ${data.attr.color};`:''}
        {data.attr.size?`font-size: ${data.attr.size};`:''}
    ">
        {data.text}
</a>
{:else}
    <span class="text {data.attr.type}" class:disabled={Boolean(data.attr.disabled)} style="
        margin: {data.attr.margin ?? 0};
        {data.attr.color?`color: ${data.attr.color};`:''}
        {data.attr.size?`font-size: ${data.attr.size};`:''}
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
    .description{
        font-size: 12px;
        &:not(a){
            color: var(--TextFillColorTertiaryBrush);
        }
    }
    .title{
        font-size: 24px;
    }
    a{
        text-decoration: none;
        color: var(--AccentFillColorSecondaryBrush);
        outline: none ;
    }
</style>