<script lang="ts">
	import { values, getValueByPath } from '../routes/+page.svelte';
	export let data: { [key: string]: any };
	const normalizeSelectType = (value: any) => String(value ?? 'Single').toLowerCase();
	const isMultipleSelectType = (value: any) => normalizeSelectType(value) === 'multiple';
	const normalizeMultipleSelection = (value: any) => Array.isArray(value)
		? value
		: value == null || value === ''
			? []
			: [value];

	$: optionValueKey = `${data.attr.optionValue}._Temp`;
	$: isMultiple = isMultipleSelectType(data.attr.selectType);
	$: selectedValues = normalizeMultipleSelection(getValueByPath($values, data.attr.optionValue));
	$: isSelected = isMultiple
		? selectedValues.some((item) => item == data.attr.value)
		: getValueByPath($values, data.attr.optionValue) == data.attr.value;
	$: if (
		!isMultiple
		&& typeof window !== 'undefined'
		&& typeof window.syncValue === 'function'
		&& isSelected
		&& getValueByPath($values, optionValueKey) !== data.text
	) {
		window.syncValue(optionValueKey, data.text);
	}

	const onClick = () => {
		if (isMultiple) {
			const current = normalizeMultipleSelection(getValueByPath($values, data.attr.optionValue));
			const exists = current.some((item) => item == data.attr.value);
			const next = exists
				? current.filter((item) => item != data.attr.value)
				: [...current, data.attr.value];
			window.syncValue(data.attr.optionValue, next);
			window.syncValue(optionValueKey, `${next.length} Selected`);
			return;
		}

		window.syncValue(data.attr.optionValue, data.attr.value);
		window.syncValue(optionValueKey, data.text);
		window.dispatchEvent(new CustomEvent('pywebwinui3-select-close', { detail: data.attr.optionValue }));
	};
</script>
<button class:select={isSelected} on:click={onClick}>
	{data.text}
</button>
<style lang="scss">
	button{
		text-align: left;
		align-self: stretch;
		border-radius: 4px;
		background-color: transparent;
		padding: 6px 12px;
		&.select,&.select:active,&:hover:not(:active){
			background-color: var(--SubtleFillColorSecondaryBrush);
		}
		&.select:hover:not(:active),&:active{
			background-color: var(--SubtleFillColorTertiaryBrush);
		}
		&.select:active::before{
			height: 6px;
		}
		&.select::before{
			position: absolute;
			content: "";
			border-radius: 1.5px;
			left: 0;
			top: 50%;
			width: 3px;
			height: 16px;
			transform: translateY(-50%);
			background-color: var(--AccentFillColorDefaultBrush);
		}
	}
</style>
