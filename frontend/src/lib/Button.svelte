<script lang="ts">
	import { values, getValueByPath } from '../routes/+page.svelte';

	export let data: { [key: string]: any };
	$: currentValue = getValueByPath($values, data.attr.value);

	const click = () => {
		if(data.attr.type=="toggle"){
			window.syncValue(data.attr.value, !currentValue)
		}else{
			window.syncValue(data.attr.value, true)
		}
	}
</script>
{#if data.attr.type=="link" && data.attr.url}
	<a
		class="main"
		class:select={false}
		class:disabled={String(data.attr.disabled??"")=="true"}
		href={data.attr.url}
		target={`_${data.attr.target ?? 'blank'}`}
		rel="noopener noreferrer"
		on:click={click}
		style="
			margin: {data.attr.margin ?? 0};
			width: {data.attr.width ?? 'fit-content'};
			height: {data.attr.height ?? 'fit-content'};
		"
	>
		{data.text} 
		<slot />
	</a>
{:else}
	<button class="main" class:select={data.attr.type=="toggle"&&currentValue} disabled={String(data.attr.disabled??"")=="true"} on:click={click} style="
		margin: {data.attr.margin ?? 0};
		width: {data.attr.width ?? 'fit-content'};
		height: {data.attr.height ?? 'fit-content'};
	">
		{data.text}
		<slot />
	</button>
{/if}
<style lang="scss">
	.main{
		display: flex;
		text-decoration: none;
		font-size: 14px;
		background-color: var(--ControlFillColorDefaultBrush);
		border-radius: 4px;
		padding: 6px 10px;
		box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
		&:hover{
			background-color: var(--ControlFillColorSecondaryBrush);
		}
		&:active{
			box-shadow: 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
			background-color: var(--ControlFillColorTertiaryBrush);
		}
		&.select{
			box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
			color: var(--TextOnAccentFillColorPrimaryBrush);
			background-color: var(--AccentFillColorDefaultBrush);
			&:hover{
				background-color: var(--AccentFillColorSecondaryBrush);
			}
			&:active{
				background-color: var(--AccentFillColorTertiaryBrush);
				color: var(--TextOnAccentFillColorSecondaryBrush);
			}
		}
	}
</style>
