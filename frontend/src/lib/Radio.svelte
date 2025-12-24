<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
</script>
<span class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
">
    {#if data.text}
        <label for="radio.{data.attr.group}.{data.attr.value}" style="
            order: {data.attr.align=="left"?0:2};
        ">
            {data.text}
        </label>
    {/if}
    <input id="radio.{data.attr.group}.{data.attr.value}" type="radio"
        checked={$values[data.attr.group]==data.attr.value}
        on:input={()=>window.syncValue(data.attr.group, data.attr.value)}
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
            border-radius: 10px;
            height: 20px;
            width: 20px;
            background-color: var(--ControlAltFillColorTransparentBrush);
            box-shadow: 0 0 0 1px var(--ControlStrongStrokeColorDefaultBrush) inset;
            appearance: none;
            &:not(:checked){
                &:hover:not(:active){
                    background-color: var(--ControlFillColorSecondaryBrush);
                }
                &:active{
                    background-color: var(--TextOnAccentFillColorPrimaryBrush);
                    box-shadow: 0 0 0 1px var(--ControlStrongStrokeColorDefaultBrush) inset, 0 0 0 5px var(--ControlSolidFillColorDefaultBrush) inset;
                }
            }
            &:checked{
                background-color: var(--TextOnAccentFillColorPrimaryBrush);
                box-shadow: 0 0 0 5px var(--AccentFillColorDefaultBrush) inset;
                &:hover:not(:active){
                    box-shadow: 0 0 0 5px var(--AccentFillColorSecondaryBrush) inset;
                }
                &:active{
                    background-color: var(--TextOnAccentFillColorSecondaryBrush);
                    box-shadow: 0 0 0 5px var(--AccentFillColorTertiaryBrush) inset;
                    
                }
            }
        }
    }
</style>