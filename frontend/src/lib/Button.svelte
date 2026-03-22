<script lang="ts">
	import { values } from '../routes/+page.svelte';
	import { openExternal } from './desktop';

	export let data: { [key: string]: any };

	const click = () => {
		if(data.attr.type=="toggle"){
			window.syncValue(data.attr.value, !$values[data.attr.value])
		}else{
			if(data.attr.type=="link"&&data.attr.url) openExternal(data.attr.url,`_${data.attr.target??'blank'}`)
			window.syncValue(data.attr.value, true)
		}
	}
</script>
<button class="main" class:select={data.attr.type=="toggle"&&$values[data.attr.value]} disabled={String(data.attr.disabled??"")=="true"} on:click={click} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'fit-content'};
	height: {data.attr.height ?? 'fit-content'};
">
	{data.text}{data.attr.type=="link"?" ":""}
	<slot />
</button>
<style lang="scss">
	.main{
		display: flex;
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