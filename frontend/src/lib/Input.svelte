<script lang="ts">
	import { values, getValueByPath } from '../routes/+page.svelte';
	export let data: { [key: string]: any };
	let ispasswordShow = false
	let padding:number

	function parseBooleanAttr(value:any, defaultValue=true){
		if (value === undefined || value === null || value === "") return defaultValue;
		if (typeof value === "boolean") return value;
		const normalized = String(value).trim().toLowerCase();
		if (["false", "0", "no", "off"].includes(normalized)) return false;
		if (["true", "1", "yes", "on"].includes(normalized)) return true;
		return defaultValue;
	}

	function parseNumberAttr(value:any){
		const number = Number(value);
		return Number.isFinite(number) ? number : null;
	}

	$: min = parseNumberAttr(data?.attr?.min);
	$: max = parseNumberAttr(data?.attr?.max);
	$: step = parseNumberAttr(data?.attr?.step) ?? 1;
	$: value = getValueByPath($values, data.attr.value);
	$: showInputButtons = parseBooleanAttr(data?.attr?.button, true);

	function clampNumber(value:number){
		let next = Number.isFinite(value) ? value : 0;
		if (min !== null) next = Math.max(next, min);
		if (max !== null) next = Math.min(next, max);
		return next;
	}

	function syncInput(raw:string){
		if(data.attr.type=="number"){
			const number = Number(raw);
			if (!Number.isFinite(number)) return;
			window.syncValue(data.attr.value, clampNumber(number));
			return;
		}
		window.syncValue(data.attr.value, raw)
	}

	function commitNumber(raw:string){
		if(data.attr.type!="number") return;
		const number = Number(raw);
		window.syncValue(data.attr.value, clampNumber(number));
	}

	function adjustNumber(delta:number){
		window.syncValue(data.attr.value, clampNumber(Number(value) + delta));
	}
</script>
<span class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
">
	<input
		type={data.attr.type=="password"?(ispasswordShow?"text":"password"):data.attr.type}
		placeholder={data.text}
		on:input={(e)=>syncInput(e.currentTarget.value)}
		on:change={(e)=>commitNumber(e.currentTarget.value)}
		on:blur={(e)=>commitNumber(e.currentTarget.value)}
		min={data.attr.min}
		max={data.attr.max}
		step={data.attr.step}
		value={value}
		style="padding-right: {(padding??10)-2}px;"
	/>
	{#if data.attr.type=="number" && showInputButtons}
		<span class="buttons" bind:clientWidth={padding}>
			<button on:click={()=>adjustNumber(step)}></button>
			<button on:click={()=>adjustNumber(-step)}></button>
		</span>
	{/if}
	{#if data.attr.type=="password" && showInputButtons}
		<span class="buttons" bind:clientWidth={padding}>
			<button on:click={()=>ispasswordShow=!ispasswordShow}>{ispasswordShow?"":""}</button>
		</span>
	{/if}
</span>
<style lang="scss">
	.buttons{
		top: 0;
		right: 0;
		padding: 5px;
		align-self: center;
		position: absolute;
		height: 100%;
		display: flex;
		gap: 5px;
		button{
			width: 25px;
			border-radius: 4px;
			color: var(--ControlStrongFillColorDefaultBrush);
			&:hover{
				background-color: var(--SubtleFillColorSecondaryBrush);
			}
			&:active{
				background-color: var(--SubtleFillColorTertiaryBrush);
			}
		}
	}
	input{
		resize: none;
		height: fit-content;
		padding: 9px 8px 9px 8px;
		border-radius: 4px;
		background-color: var(--ControlFillColorDefaultBrush);
		border: 1px solid var(--ControlStrokeColorDefaultBrush);
		border-bottom: 1.5px solid var(--ControlStrongFillColorDefaultBrush);
		line-height: 1.3em;
		transition: all 0.2s ease, padding 0s, border-bottom-width 0s, width 0s, height 0s;
		width: 100%;
		height: 100%;
		&::-webkit-inner-spin-button,&::-webkit-outer-spin-button{
			appearance: none;
			margin: 0;
		}
		&::placeholder {
			color: var(--ControlStrongFillColorDefaultBrush);
			opacity: 1;
		}
		&:hover:not(:focus){
			background-color: var(--ControlFillColorSecondaryBrush);
		}
		&:focus{
			background-color: var(--ControlFillColorInputActiveBrush);
			padding: 9px 8px 8px 8px;
			border-bottom-width: 2.5px;
			border-bottom-color: var(--AccentFillColorDefaultBrush);
		}
	}
</style>
