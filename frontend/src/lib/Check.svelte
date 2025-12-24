<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
    $: value = +$values[data.attr.value] || 0
    $: checked = value==1
    $: indeterminate = value==2
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
        bind:checked={checked}
        bind:indeterminate={indeterminate}
        on:input|preventDefault={()=>window.syncValue(data.attr.value, (value+1)%(data.attr.type=="three"?3:2))}
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
            &:checked,&:indeterminate{
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
                &:checked::before{
                    content: '';
                }
                &:indeterminate::before{
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