<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span class:disabled={Boolean(data.attr.disabled)}>
    {#if data.text}
        <label for="radio.{data.attr.group}.{data.attr.value}" style="
            order: {data.attr.aligin=="left"?0:2};
        ">
            {data.text}
        </label>
    {/if}
    <input id="radio.{data.attr.group}.{data.attr.value}" type="radio"
        checked={$values[data.attr.group]==data.attr.value}
        on:input={()=>window.setValue(data.attr.group, data.attr.value)}
    />
</span>
<style lang="scss">
    $light: (
        Radio-InnerColor: #ededed,
        Radio-BorderColor: #858585,
        Radio-HoverInnerColor: #e5e5e5,
        Radio-ActiveOuterColor: #dcdcdc,
        Radio-ActiveBorderColor: #b1b1b1,
    );
    $dark: (
        Radio-InnerColor: #272727,
        Radio-BorderColor: #9e9e9e,
        Radio-HoverInnerColor: #343434,
        Radio-ActiveOuterColor: #3a3a3a,
        Radio-ActiveBorderColor: #565656,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    span{
        display: flex;
        gap: 4px;
        align-items: center;
        label{
            cursor: pointer;
        }
        input{
            cursor: pointer;
            order: 1;
            border-radius: 10px;
            height: 20px;
            width: 20px;
            background-color: var(--Radio-InnerColor);
            box-shadow: 0 0 0 1px var(--Radio-BorderColor) inset;
            appearance: none;
            &:hover:not(:active){
                background-image: linear-gradient(var(--Radio-HoverInnerColor));
            }
            &:active{
                background-color: var(--TextOnAccentFillColorPrimaryBrush);
                box-shadow: 0 0 0 1px var(--Radio-ActiveBorderColor) inset, 0 0 0 5px var(--Radio-ActiveOuterColor) inset;
            }
            &:checked{
                background-color: var(--TextOnAccentFillColorPrimaryBrush);
                box-shadow: 0 0 0 5px var(--AccentFillColorSecondaryBrush) inset;
                &:hover:not(:active){
                    background-image: linear-gradient(var(--ButtonFillColor));
                    box-shadow: 0 0 0 4px var(--AccentFillColorSecondaryBrush) inset;
                }
                &:active{
                    background-image: linear-gradient(var(--ButtonFillColor));
                    
                }
            }
        }
    }
</style>