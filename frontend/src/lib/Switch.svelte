<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
</script>
<span class="main" class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
">
    <span style="
        order: {data.attr.align=="right"?2:0};
        align-items: {data.attr.align=="right"?'flex-start':'flex-end'};
    ">
        <label for="switch.{data.attr.value}" style="
            opacity: {$values[data.attr.value]?'1':'0'};
        ">
            {data.attr.on??'ON'}
        </label>
        <label for="switch.{data.attr.value}" style="
            opacity: {$values[data.attr.value]?'0':'1'};
        ">
            {data.attr.off??'OFF'}
        </label>
    </span>
    <input id="switch.{data.attr.value}" type="checkbox" checked={$values[data.attr.value]} on:input={()=>{window.syncValue(data.attr.value, !$values[data.attr.value])}}/>
</span>
<style lang="scss">
    .main{
        display: flex;
        align-self: center;
        align-items: center;
        span{
            display: flex;
            flex-direction: column;
            cursor: pointer;
            user-select: none;
            height: 1.2em;
            padding: 0px 5px;
            &:hover{
                color: var(--TextFillColorSecondaryBrush);
            }
            label{
                height: 0;
            }
        }
        input{
            order: 1;
            appearance: none;
            background-color: var(--ControlAltFillColorTransparentBrush);
            width: 48px;
            border-radius: 12px;
            box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlStrongStrokeColorDefaultBrush) inset;
            height: 24px;
            cursor: pointer;
            &::before{
                display: flex;
                margin: 5.5px;
                content: "";
                background-color: var(--ControlStrongFillColorDefaultBrush);
                width: 13px;
                border-radius: 7px;
                height: 13px;
                box-shadow: 0 0 0 13px var(--ControlStrongFillColorDefaultBrush) inset;
            }
            &:hover{
                background-color: var(--ControlAltFillColorTertiaryBrush);
                &::before{
                    box-shadow: 0 0 0 1px var(--ControlStrongFillColorDefaultBrush), 0 0 0 1px var(--ControlStrongFillColorDefaultBrush), 0 0 0 13px var(--ControlStrongFillColorDefaultBrush) inset;
                }
            }
            &:active{
                background-color: var(--ControlAltFillColorQuarternaryBrush);
                &::before{
                    width: 22px;
                }
            }
            &:checked{
                background-color: var(--AccentFillColorDefaultBrush);
                box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
                &::before{
                    background-color: var(--TextOnAccentFillColorPrimaryBrush);
                    justify-self: right;
                    box-shadow: none;
                }
                &:hover{
                    background-color: var(--AccentFillColorSecondaryBrush);
                    &::before{
                        box-shadow: 0 0 0 2px var(--TextOnAccentFillColorPrimaryBrush);
                    }
                }
            }
        }
    }
</style>