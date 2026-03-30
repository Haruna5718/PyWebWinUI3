<script lang="ts">
	import { values, formatComponentSource } from '../routes/+page.svelte';
	import Component from './Component.svelte';
	export let data: { [key: string]: any };
	type ComponentNode = Record<string, any>;

	const formatOption = (targetData:any) => {
		let isChange = targetData.tag == "Option";
		return {
			tag: targetData.tag,
			attr: { ...targetData.attr, ...(isChange ? { optionValue: data.attr.value } : {}) },
			text: targetData.text,
			child: targetData.child.map(formatOption)
		};
	};

	const formatIndex = (text: any, index: number) =>
		String(text).replace(/(?<!\\){i}/g, () => String(index)).replace(/\\({i})/g, "$1");

	const formatIndexAll = (targetData: ComponentNode, index: number): ComponentNode => ({
		tag: targetData.tag,
		attr: Object.fromEntries(Object.entries(targetData.attr ?? {}).map(([key, value]) => [key, formatIndex(value, index)])),
		text: formatIndex(targetData.text, index),
		child: (targetData.child ?? []).map((child: ComponentNode) => formatIndexAll(child, index))
	});

	const findSelectedTextFromChildren = (children: ComponentNode[], currentValue: any): string => {
		for (const rawChild of children) {
			const child = formatComponentSource(rawChild);

			if (String(child?.attr?.disabled ?? "") === "true") {
				continue;
			}

			if (child?.tag === "Option") {
				if (child.attr?.value == currentValue) {
					return child.text ?? '';
				}
				continue;
			}

			if (child?.tag === "If") {
				const condition = (child.attr?.raw ?? child.attr?.data) ? "True" : "False";
				const branch = child.child?.find((item: ComponentNode) => item.tag === condition);
				if (branch) {
					const text = findSelectedTextFromChildren(branch.child ?? [], currentValue);
					if (text) {
						return text;
					}
				}
				continue;
			}

			if (child?.tag === "Match") {
				const branch = child.child?.find((item: ComponentNode) => child.attr?.data == item.attr?.target)
					?? child.child?.find((item: ComponentNode) => !item.attr?.target);
				if (branch) {
					const text = findSelectedTextFromChildren(branch.child ?? [], currentValue);
					if (text) {
						return text;
					}
				}
				continue;
			}

			if (child?.tag === "Repeat") {
				const repeatCount = Number(child.attr?.data) || 0;
				for (let index = 0; index < repeatCount; index += 1) {
					const repeatedChildren = (rawChild.child ?? []).map((repeatChild: ComponentNode) => formatIndexAll(repeatChild, index));
					const text = findSelectedTextFromChildren(repeatedChildren, currentValue);
					if (text) {
						return text;
					}
				}
				continue;
			}

			if (child?.child?.length) {
				const text = findSelectedTextFromChildren(child.child, currentValue);
				if (text) {
					return text;
				}
			}
		}

		return '';
	};

	let open=false
	let main:HTMLButtonElement
	let formattedChildren: Record<string, any>[] = [];
	let optionValueKey = '';
	let selectedText = '';

	$: formattedChildren = open
		? data.child.map((child: Record<string, any>) => formatOption(formatComponentSource(child)))
		: [];
	$: optionValueKey = `${data.attr.value}._Temp`;
	$: {
		const currentValue = $values[data.attr.value];
		const tempValue = $values[optionValueKey];
		const resolvedSelectedText = findSelectedTextFromChildren(data.child ?? [], currentValue);
		const nextSelectedText = resolvedSelectedText || tempValue || '';

		selectedText = nextSelectedText;

		if (
			typeof window !== 'undefined'
			&& typeof window.syncValue === 'function'
			&& nextSelectedText
			&& tempValue !== nextSelectedText
		) {
			window.syncValue(optionValueKey, nextSelectedText);
		}
	}
</script>
<svelte:window on:click={(e)=>{if(!main?.contains(e.target as Node | null))open=false}}></svelte:window>
<span class="container" class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
">
	<button class="main" on:click={()=>{open=!open}} bind:this={main}>
		<p>
			{data.text?`${data.text}: `:''}{selectedText}
		</p>
		<span></span>
	</button>
	<div class="menu" style="display: {open?'flex':'none'};">
		{#each formattedChildren as childData}
			<Component formatData={childData} />
		{/each}
	</div>
</span>
<style lang="scss">
	@keyframes onAnim {
		0%{
			transform: translateY(0px);
		}
		100%{
			transform: translateY(10px);
		}
	}
	.main{
		width: 100%;
		height: 100%;
		display: flex;
		justify-content: space-between;
		font-size: 14px;
		background-color: var(--ControlFillColorDefaultBrush);
		border-radius: 4px;
		padding: 6px 10px;
		box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
		&:hover{
			background-color: var(--ControlFillColorSecondaryBrush);
		}
		&:active{
			color: currentColor;
			box-shadow: 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
			background-color: var(--ControlFillColorTertiaryBrush);
			span{
				transform: translateY(2px);
			}
		}
		span{
			margin-left: 4px;
			align-items: center;
		}
	}
	.menu{
		display: flex;
		flex-direction: column;
		animation : onAnim 0.2s ease-out forwards alternate;
		z-index: 100;
		padding: 4px;
		background-color: var(--SolidBackgroundFillColorQuarternaryBrush);
		border: 1.5px solid var(--SurfaceStrokeColorFlyoutBrush);
		border-radius: 8px;
		position: absolute;
		left: 50%;
		translate: -50%;
		gap: 5px;
		width: max-content;
		max-height: 50vh;
		overflow-x: hidden;
		overflow-y: auto;
		box-shadow: 0 1px 1px 0 var(--SmokeFillColorDefaultBrush);
	}
</style>
