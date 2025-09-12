<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    let value,checked,indeterminate;
    $:{
        value = Number($values[data.attr.value]??0)
        checked = value==1
        indeterminate = value==2
    }
</script>
<span>
    {#if data.text}
        <label for="check.{data.attr.value}" style="
            order: {data.attr.aligin=="left"?0:2};
        ">
            {data.text}
        </label>
    {/if}
    <input id="check.{data.attr.value}" type="checkbox"
        bind:checked={checked}
        bind:indeterminate={indeterminate}
        on:input|preventDefault={()=>window.setValue(data.attr.value, (value+1)%(data.attr.type=="three"?3:2))}
    />
</span>
<style lang="scss">
    $light: (
        Check-FillColor: #ededed,
        Check-HoverColor: #e5e5e5,
        Check-ActiveColor: #dcdcdc,
        Check-BorderColor: #858585,
        Check-BorderActiveColor: #b1b1b1,
    );
    $dark: (
        Check-FillColor: #272727,
        Check-HoverColor: #343434,
        Check-ActiveColor: #3a3a3a,
        Check-BorderColor: #9e9e9e,
        Check-BorderActiveColor: #4f4f4f,
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
            user-select: none;
        }
        input{
            cursor: pointer;
            order: 1;
            border-radius: 4px;
            height: 20px;
            width: 20px;
            background-color: var(--Check-FillColor);
            box-shadow: 0 0 0 1px var(--Check-BorderColor) inset;
            appearance: none;
            &:hover{
                background-color: var(--Check-HoverColor);
            }
            &:active{
                background-color: var(--Check-ActiveColor);
                box-shadow: 0 0 0 1px var(--Check-BorderActiveColor) inset;
            }
            &:checked,&:indeterminate{
                background-color: var(--AccentFillColorSecondaryBrush);
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
                    background-image: linear-gradient(var(--AccentHoverCoverColor));
                }
                &:active{
                    background-image: linear-gradient(var(--AccentActiveCoverColor));
                }
            }
        }
    }
</style>