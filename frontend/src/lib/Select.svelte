<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { values, formatComponentSource, getValueByPath } from '../routes/+page.svelte';
	import Component from './Component.svelte';
	export let data: { [key: string]: any };
	type ComponentNode = Record<string, any>;
	const normalizeSelectType = (value: any) => String(value ?? 'Single').toLowerCase();
	const isMultipleSelectType = (value: any) => normalizeSelectType(value) === 'multiple';
	const normalizeMultipleSelection = (value: any) => Array.isArray(value)
		? value
		: value == null || value === ''
			? []
			: [value];

	const formatOption = (targetData:any) => {
		let isChange = targetData.tag == "Option";
		return {
			tag: targetData.tag,
			attr: { ...targetData.attr, ...(isChange ? { optionValue: data.attr.value, selectType: data.attr.type ?? 'Single' } : {}) },
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

	const hasSelectableOption = (children: ComponentNode[]): boolean => {
		for (const rawChild of children) {
			const child = formatComponentSource(rawChild);

			if (String(child?.attr?.disabled ?? "") === "true") {
				continue;
			}

			if (child?.tag === "Option") {
				return true;
			}

			if (child?.tag === "If") {
				const condition = (child.attr?.raw ?? child.attr?.data) ? "True" : "False";
				const branch = child.child?.find((item: ComponentNode) => item.tag === condition);
				if (branch && hasSelectableOption(branch.child ?? [])) {
					return true;
				}
				continue;
			}

			if (child?.tag === "Match") {
				const branch = child.child?.find((item: ComponentNode) => child.attr?.data == item.attr?.target)
					?? child.child?.find((item: ComponentNode) => !item.attr?.target);
				if (branch && hasSelectableOption(branch.child ?? [])) {
					return true;
				}
				continue;
			}

			if (child?.tag === "Repeat") {
				const repeatCount = Number(child.attr?.data) || 0;
				for (let index = 0; index < repeatCount; index += 1) {
					const repeatedChildren = (rawChild.child ?? []).map((repeatChild: ComponentNode) => formatIndexAll(repeatChild, index));
					if (hasSelectableOption(repeatedChildren)) {
						return true;
					}
				}
				continue;
			}

			if (child?.child?.length && hasSelectableOption(child.child)) {
				return true;
			}
		}

		return false;
	};

	const countSelectedOptionsFromChildren = (children: ComponentNode[], selectedValues: any[]): number => {
		let count = 0;

		for (const rawChild of children) {
			const child = formatComponentSource(rawChild);

			if (String(child?.attr?.disabled ?? "") === "true") {
				continue;
			}

			if (child?.tag === "Option") {
				if (selectedValues.some((item) => item == child.attr?.value)) {
					count += 1;
				}
				continue;
			}

			if (child?.tag === "If") {
				const condition = (child.attr?.raw ?? child.attr?.data) ? "True" : "False";
				const branch = child.child?.find((item: ComponentNode) => item.tag === condition);
				if (branch) {
					count += countSelectedOptionsFromChildren(branch.child ?? [], selectedValues);
				}
				continue;
			}

			if (child?.tag === "Match") {
				const branch = child.child?.find((item: ComponentNode) => child.attr?.data == item.attr?.target)
					?? child.child?.find((item: ComponentNode) => !item.attr?.target);
				if (branch) {
					count += countSelectedOptionsFromChildren(branch.child ?? [], selectedValues);
				}
				continue;
			}

			if (child?.tag === "Repeat") {
				const repeatCount = Number(child.attr?.data) || 0;
				for (let index = 0; index < repeatCount; index += 1) {
					const repeatedChildren = (rawChild.child ?? []).map((repeatChild: ComponentNode) => formatIndexAll(repeatChild, index));
					count += countSelectedOptionsFromChildren(repeatedChildren, selectedValues);
				}
				continue;
			}

			if (child?.child?.length) {
				count += countSelectedOptionsFromChildren(child.child, selectedValues);
			}
		}

		return count;
	};

	let open=false
	let main:HTMLButtonElement
	let container:HTMLSpanElement
	let menu:HTMLDivElement
	let formattedChildren: Record<string, any>[] = [];
	let optionValueKey = '';
	let selectedText = '';
	let hasOptions = false;
	let isMultiple = false;
	let forcedDisplayText = '';
	let menuOffsetX = 0;
	let menuMaxHeight = 0;
	let menuDirection:'down'|'up' = 'down';
	const menuAnimationOffset = 10;

	const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max);

	const getMinimumVisibleHeight = () => {
		if (!menu) {
			return 0;
		}

		const optionElements = Array.from(menu.children)
			.filter((node): node is HTMLElement => node instanceof HTMLElement)
			.slice(0, 2);
		if (optionElements.length === 0) {
			return 0;
		}

		const style = window.getComputedStyle(menu);
		const gap = parseFloat(style.rowGap || style.gap || '0') || 0;
		const paddingTop = parseFloat(style.paddingTop || '0') || 0;
		const paddingBottom = parseFloat(style.paddingBottom || '0') || 0;
		const borderTop = parseFloat(style.borderTopWidth || '0') || 0;
		const borderBottom = parseFloat(style.borderBottomWidth || '0') || 0;
		const itemsHeight = optionElements.reduce((sum, element) => sum + element.getBoundingClientRect().height, 0);

		return itemsHeight
			+ paddingTop
			+ paddingBottom
			+ borderTop
			+ borderBottom
			+ gap * Math.max(0, optionElements.length - 1);
	};

	const getClipBoundary = () => {
		let parent = container?.parentElement ?? null;
		while (parent) {
			const style = window.getComputedStyle(parent);
			const overflowX = style.overflowX;
			const overflowY = style.overflowY;
			if (
				['hidden', 'scroll', 'auto', 'clip'].includes(overflowX)
				|| ['hidden', 'scroll', 'auto', 'clip'].includes(overflowY)
			) {
				const rect = parent.getBoundingClientRect();
				return {
					left: rect.left,
					right: rect.left + parent.clientWidth,
					top: rect.top,
					bottom: rect.top + parent.clientHeight
				};
			}
			parent = parent.parentElement;
		}

		return {
			left: 0,
			right: document.documentElement.clientWidth,
			top: 0,
			bottom: document.documentElement.clientHeight
		};
	};

	const updateMenuBounds = async () => {
		if (!open || !menu) {
			return;
		}

		await tick();
		if (!open || !menu) {
			return;
		}

		const boundaryPadding = 8;
		const boundary = getClipBoundary();
		const containerRect = container?.getBoundingClientRect();
		if (!containerRect) {
			return;
		}
		const minimumVisibleHeight = getMinimumVisibleHeight();
		const spaceBelow = boundary.bottom - containerRect.bottom - boundaryPadding - menuAnimationOffset;

		menuDirection = spaceBelow < minimumVisibleHeight ? 'up' : 'down';

		await tick();
		if (!open || !menu) {
			return;
		}

		const rect = menu.getBoundingClientRect();
		const baseLeft = rect.left - menuOffsetX;
		const baseRight = baseLeft + rect.width;

		let nextOffsetX = 0;
		if (baseLeft < boundary.left + boundaryPadding) {
			nextOffsetX = (boundary.left + boundaryPadding) - baseLeft;
		} else if (baseRight > boundary.right - boundaryPadding) {
			nextOffsetX = (boundary.right - boundaryPadding) - baseRight;
		}

		menuOffsetX = nextOffsetX;

		await tick();
		if (!open || !menu) {
			return;
		}

		const availableHeight = menuDirection === 'up'
			? Math.max(0, containerRect.top - boundary.top - boundaryPadding - menuAnimationOffset)
			: Math.max(0, boundary.bottom - containerRect.bottom - boundaryPadding - menuAnimationOffset);
		menuMaxHeight = availableHeight;
	};

	const handleMenuWheel = (event: WheelEvent) => {
		if (!menu || event.ctrlKey) {
			return;
		}

		const maxScrollTop = Math.max(0, menu.scrollHeight - menu.clientHeight);
		if (maxScrollTop <= 0) {
			event.preventDefault();
			event.stopPropagation();
			return;
		}

		const nextScrollTop = clamp(menu.scrollTop + event.deltaY, 0, maxScrollTop);
		menu.scrollTop = nextScrollTop;
		event.preventDefault();
		event.stopPropagation();

	};

	onMount(() => {
		const closeHandler = (event: Event) => {
			const selectCloseEvent = event as CustomEvent<string>;
			if (selectCloseEvent.detail === data.attr.value) {
				open = false;
			}
		};

		const refreshBounds = () => {
			if (open) {
				void updateMenuBounds();
			}
		};

		window.addEventListener('pywebwinui3-select-close', closeHandler as EventListener);
		window.addEventListener('resize', refreshBounds);
		window.addEventListener('scroll', refreshBounds, true);
		return () => {
			window.removeEventListener('pywebwinui3-select-close', closeHandler as EventListener);
			window.removeEventListener('resize', refreshBounds);
			window.removeEventListener('scroll', refreshBounds, true);
		};
	});

	$: formattedChildren = open
		? data.child.map((child: Record<string, any>) => formatOption(formatComponentSource(child)))
		: [];
	$: optionValueKey = `${data.attr.value}._Temp`;
	$: isMultiple = isMultipleSelectType(data.attr.type);
	$: hasOptions = hasSelectableOption(data.child ?? []);
	$: forcedDisplayText = data.attr.displayValue
		? String(getValueByPath($values, data.attr.displayValue) ?? data.attr.displayValue ?? '')
		: '';
	$: if (!hasOptions && open) {
		open = false;
	}
	$: if (open) {
		void updateMenuBounds();
	} else {
		menuOffsetX = 0;
		menuMaxHeight = 0;
		menuDirection = 'down';
	}
	$: {
		const currentValue = getValueByPath($values, data.attr.value);
		const tempValue = getValueByPath($values, optionValueKey);
		const currentSelectedValues = normalizeMultipleSelection(currentValue);
		const resolvedSelectedText = isMultiple
			? `${countSelectedOptionsFromChildren(data.child ?? [], currentSelectedValues)} Selected`
			: findSelectedTextFromChildren(data.child ?? [], currentValue);
		const nextSelectedText = forcedDisplayText || resolvedSelectedText || tempValue || (isMultiple ? '0 Selected' : '');

		selectedText = nextSelectedText;

		if (
			!forcedDisplayText &&
			typeof window !== 'undefined'
			&& typeof window.syncValue === 'function'
			&& nextSelectedText
			&& tempValue !== nextSelectedText
		) {
			window.syncValue(optionValueKey, nextSelectedText);
		}
	}
</script>
<svelte:window on:click={(e)=>{if(!container?.contains(e.target as Node | null))open=false}}></svelte:window>
<span class="container" class:disabled={String(data.attr.disabled??"")=="true"} style="
	margin: {data.attr.margin ?? 0};
	width: {data.attr.width ?? 'auto'};
	height: {data.attr.height ?? 'auto'};
" bind:this={container}>
	<button class="main" on:click={()=>{if(hasOptions && String(data.attr.disabled??"")!="true")open=!open}} bind:this={main}>
		<p>
			{data.text?`${data.text}: `:''}{selectedText}
		</p>
		<span></span>
	</button>
	<div class="menu" class:up={menuDirection === 'up'} bind:this={menu} on:wheel={handleMenuWheel} style="display: {open&&hasOptions?'flex':'none'}; translate: calc(-50% + {menuOffsetX}px) 0; max-height: {menuMaxHeight ? `${menuMaxHeight}px` : '50vh'};">
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
	@keyframes onAnimUp {
		0%{
			transform: translateY(0px);
		}
		100%{
			transform: translateY(-10px);
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
		gap: 5px;
		width: max-content;
		max-height: 50vh;
		overflow-x: hidden;
		overflow-y: auto;
		overscroll-behavior: contain;
		box-shadow: 0 1px 1px 0 var(--SmokeFillColorDefaultBrush);
		left: 50%;
		top: calc(100% + 4px);
		translate: -50%;
		transition: all 0.2s ease, color 0.1s ease, width 0s, height 0s, max-height 0s, translate 0s, transform 0s;
		&.up{
			animation-name: onAnimUp;
			top: auto;
			bottom: calc(100% + 4px);
		}
	}
</style>
