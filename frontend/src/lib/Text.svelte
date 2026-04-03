<script lang="ts">
	import { openLink } from './desktop';

	export let data: { [key: string]: any };

	const click = (event: MouseEvent) => {
		if (!data.attr.url) return;
		event.preventDefault();
		openLink(data.attr.url, `_${data.attr.target ?? 'blank'}`);
	};
</script>

{#if data.attr.url}
	<a class="text {data.attr.type}" class:disabled={String(data.attr.disabled??"")=="true"} target="_{data.attr.target??'blank'}" href={data.attr.url} on:click={click} style="
			margin: {data.attr.margin ?? 0};
			{data.attr.color?`color: ${data.attr.color};`:''}
			{data.attr.size?`font-size: ${data.attr.size};`:''}
		">
			{data.text}
	</a>
{:else}
	<p class="text {data.attr.type}" class:disabled={String(data.attr.disabled??"")=="true"} style="
			margin: {data.attr.margin ?? 0};
			{data.attr.color?`color: ${data.attr.color};`:''}
			{data.attr.size?`font-size: ${data.attr.size};`:''}
		">
			{data.text}
	</p>
{/if}
<style lang="scss">
	.text{
		word-wrap: break-word;
		white-space: pre-wrap;
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
		color: var(--AccentTextFillColorPrimaryBrush);
		outline: none ;
	}
</style>
