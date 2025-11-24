<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span class="main" class:disabled={String(data.attr.disabled??"")=="true"}>
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
    <input id="switch.{data.attr.value}" type="checkbox" checked={$values[data.attr.value]} on:input={()=>{window.setValue(data.attr.value, !$values[data.attr.value])}}/>
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
            height: 1.4em;
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
            width: 46px;
            border-radius: 12px;
            box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1.5px var(--ControlStrongStrokeColorDefaultBrush) inset;
            height: 24px;
            cursor: pointer;
            &::before{
                content: "";
                margin: 5px;
                position: absolute;
                background-color: var(--ControlStrongFillColorDefaultBrush);
                width: 14px;
                border-radius: 8px;
                height: 14px;
                transform: translateX(0px);
            }
            &:hover{
                background-color: var(--ControlAltFillColorTertiaryBrush);
                &::before{
                    background-color: var(--ControlStrongFillColorDefaultBrush);
                    box-shadow: 0 0 0 1px var(--ControlStrongFillColorDefaultBrush);
                }
            }
            &:active{
                background-color: var(--ControlAltFillColorQuarternaryBrush);
                &::before{
                    width: 19px;
                }
            }
            &:checked{
                background-color: var(--AccentFillColorDefaultBrush);
                box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
                &::before{
                    background-color: var(--TextOnAccentFillColorPrimaryBrush);
                    transform: translateX(22px);
                }
                &:hover{
                    background-color: var(--AccentFillColorSecondaryBrush);
                    &::before{
                        box-shadow: 0 0 0 1px var(--TextOnAccentFillColorPrimaryBrush);
                    }
                }
                &:active{
                    background-color: var(--AccentFillColorTertiaryBrush);
                    &::before{
                        transform: translateX(17px);
                    }
                }
            }
        }
    }
</style>