<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span class="main">
    <span style="
        order: {data.attr.aligin=="right"?2:0};
        align-items: {data.attr.aligin=="right"?'flex-start':'flex-end'};
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
    $light: (
        Switch-FillColor: #f7f7f7,
        Switch-FillHoverColor: #eeeeee,
        Switch-FillActiveColor: #e5e5e5,
        Switch-BorderColor: #5e5e5e,
        Switch-BorderHoverColor: #5b5b5b,
    );
    $dark: (
        Switch-FillColor: #2d2d2d,
        Switch-FillHoverColor: #3b3b3b,
        Switch-FillActiveColor: #414141,
        Switch-BorderColor: #cfcfcf,
        Switch-BorderHoverColor: #d3d3d3,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

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
            background-color: var(--Switch-FillColor);
            width: 46px;
            border-radius: 12px;
            box-shadow: 0 1px 0 0 #00000030, 0 0 0 1.5px var(--Switch-BorderColor) inset;
            height: 24px;
            cursor: pointer;
            &::before{
                content: "";
                margin: 5px;
                position: absolute;
                background-color: var(--Switch-BorderColor);
                width: 14px;
                border-radius: 8px;
                height: 14px;
                transform: translateX(0px);
            }
            &:hover{
                background-color: var(--Switch-FillHoverColor);
                &::before{
                    background-color: var(--Switch-BorderHoverColor);
                    box-shadow: 0 0 0 1px var(--Switch-BorderHoverColor);
                }
            }
            &:active{
                background-color: var(--Switch-FillActiveColor);
                &::before{
                    width: 19px;
                }
            }
            &:checked{
                background-color: var(--AccentFillColorSecondaryBrush);
                box-shadow: 0 1px 0 0 #00000030;
                &::before{
                    background-color: var(--TextOnAccentFillColorPrimaryBrush);
                    transform: translateX(22px);
                }
                &:hover{
                    background-image: linear-gradient(var(--AccentHoverCoverColor));
                    &::before{
                        box-shadow: 0 0 0 1px var(--TextOnAccentFillColorPrimaryBrush);
                    }
                }
                &:active{
                    background-image: linear-gradient(var(--AccentActiveCoverColor));
                    &::before{
                        transform: translateX(17px);
                    }
                }
            }
        }
    }
</style>