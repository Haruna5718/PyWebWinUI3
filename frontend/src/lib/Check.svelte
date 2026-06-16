<script lang="ts">
    import { values, getValueByPath } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
    let input: HTMLInputElement;

    $: value = +getValueByPath($values, data.attr.value) || 0;
    $: isThreeState = data.attr.type == "three";
    $: checked = value == 1;
    $: indeterminate = isThreeState && value == 2;
    $: if (input) {
        input.indeterminate = indeterminate;
    }

    function toggle() {
        const maxState = isThreeState ? 3 : 2;
        const normalizedValue = ((value % maxState) + maxState) % maxState;
        window.syncValue(data.attr.value, (normalizedValue + 1) % maxState);
    }
</script>
<span class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
">
    {#if data.text}
        <label for="check.{data.attr.value}" style="
            order: {data.attr.align=="left"?0:2};
        ">
            {data.text}
        </label>
    {/if}
    <input id="check.{data.attr.value}" type="checkbox"
        bind:this={input}
        checked={checked}
        class:checked
        class:indeterminate
        aria-checked={indeterminate ? "mixed" : checked ? "true" : "false"}
        on:click|preventDefault={toggle}
    />
</span>
<style lang="scss">
    span{
        display: flex;
        gap: 4px;
        align-items: center;
        input{
            cursor: pointer;
            order: 1;
            border-radius: 4px;
            height: 20px;
            width: 20px;
            background-color: var(--ControlAltFillColorTransparentBrush);
            box-shadow: 0 0 0 1px var(--ControlStrongStrokeColorDefaultBrush) inset;
            appearance: none;
            &:hover{
                background-color: var(--ControlAltFillColorTertiaryBrush);
            }
            &:active{
                background-color: var(--ControlAltFillColorQuarternaryBrush);
            }
            &.checked,&.indeterminate{
                background-color: var(--AccentFillColorDefaultBrush);
                box-shadow: none;
                &::before{
                    font-weight: bold;
                    position: absolute;
                    inset: 0;
                    line-height: 20px;
                    text-align: center;
                    color: var(--TextOnAccentFillColorPrimaryBrush);
                }
                &.checked::before{
                    content: '';
                }
                &.indeterminate::before{
                    content: '';
                }
                &:hover{
                    background-color: var(--AccentFillColorSecondaryBrush);
                }
                &:active{
                    background-color: var(--AccentFillColorTertiaryBrush);
                }
            }
        }
    }
</style>
