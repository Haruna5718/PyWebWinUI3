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
			--button-padding: {data.attr.padding ?? '6px 10px'};
			--button-radius: {data.attr.round ?? '4px'};
			--button-color: {data.attr.color ?? 'inherit'};
			--button-background: {data.attr.background ?? 'var(--ControlFillColorDefaultBrush)'};
			--button-hover-background: {data.attr.hoverBackground ?? 'var(--ControlFillColorSecondaryBrush)'};
			--button-active-background: {data.attr.activeBackground ?? 'var(--ControlFillColorTertiaryBrush)'};
			--button-border-color: {data.attr.borderColor ?? 'var(--ControlStrokeColorDefaultBrush)'};
			--button-shadow: {data.attr.shadow ?? '0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--button-border-color) inset'};
			--button-select-color: {data.attr.selectColor ?? 'var(--TextOnAccentFillColorPrimaryBrush)'};
			--button-select-background: {data.attr.selectBackground ?? 'var(--AccentFillColorDefaultBrush)'};
			--button-select-hover-background: {data.attr.selectHoverBackground ?? 'var(--AccentFillColorSecondaryBrush)'};
			--button-select-active-background: {data.attr.selectActiveBackground ?? 'var(--AccentFillColorTertiaryBrush)'};
			--button-select-active-color: {data.attr.selectActiveColor ?? 'var(--TextOnAccentFillColorSecondaryBrush)'};
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
		--button-padding: {data.attr.padding ?? '6px 10px'};
		--button-radius: {data.attr.round ?? '4px'};
		--button-color: {data.attr.color ?? 'inherit'};
		--button-background: {data.attr.background ?? 'var(--ControlFillColorDefaultBrush)'};
		--button-hover-background: {data.attr.hoverBackground ?? 'var(--ControlFillColorSecondaryBrush)'};
		--button-active-background: {data.attr.activeBackground ?? 'var(--ControlFillColorTertiaryBrush)'};
		--button-border-color: {data.attr.borderColor ?? 'var(--ControlStrokeColorDefaultBrush)'};
		--button-shadow: {data.attr.shadow ?? '0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--button-border-color) inset'};
		--button-select-color: {data.attr.selectColor ?? 'var(--TextOnAccentFillColorPrimaryBrush)'};
		--button-select-background: {data.attr.selectBackground ?? 'var(--AccentFillColorDefaultBrush)'};
		--button-select-hover-background: {data.attr.selectHoverBackground ?? 'var(--AccentFillColorSecondaryBrush)'};
		--button-select-active-background: {data.attr.selectActiveBackground ?? 'var(--AccentFillColorTertiaryBrush)'};
		--button-select-active-color: {data.attr.selectActiveColor ?? 'var(--TextOnAccentFillColorSecondaryBrush)'};
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
		color: var(--button-color);
		background-color: var(--button-background);
		border-radius: var(--button-radius);
		padding: var(--button-padding);
		box-shadow: var(--button-shadow);
		&:hover{
			background-color: var(--button-hover-background);
		}
		&:active{
			box-shadow: 0 0 0 1px var(--button-border-color) inset;
			background-color: var(--button-active-background);
		}
		&.select{
			box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
			color: var(--button-select-color);
			background-color: var(--button-select-background);
			&:hover{
				background-color: var(--button-select-hover-background);
			}
			&:active{
				background-color: var(--button-select-active-background);
				color: var(--button-select-active-color);
			}
		}
		&.disabled{
			opacity: 0.7;
			pointer-events: none;
		}
	}
</style>
