<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };

    if ($values[data.attr.optionValue]==data.attr.value) window.setValue(`${data.attr.optionValue}._Option`, data.text);
</script>
<button style={data.attr.style} class:select={$values[data.attr.optionValue]==data.attr.value} on:click={()=>{window.setValue(data.attr.optionValue, data.attr.value);window.setValue(`${data.attr.optionValue}._Option`, data.text)}}>
    {data.text}
</button>
<style lang="scss">
    $light: (
        SelectOption-HoverColor: #f0f0f0,
        SelectOption-ActiveColor: #f3f3f3,
    );
    $dark: (
        SelectOption-HoverColor: #383838,
        SelectOption-ActiveColor: #343434,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    button{
        text-align: left;
        align-self: stretch;
        border-radius: 4px;
        background-color: transparent;
        padding: 6px 12px;
        &.select,&.select:active,&:hover:not(:active){
            background-color: var(--SelectOption-HoverColor);
        }
        &.select:hover:not(:active),&:active{
            background-color: var(--SelectOption-ActiveColor);
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
            background-color: var(--AccentFillColorSecondaryBrush);
        }
    }
</style>