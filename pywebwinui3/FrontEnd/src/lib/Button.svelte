<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    const click = () => {
        if(data.attr.type=="toggle"){
            window.setValue(data.attr.value, !$values[data.attr.value])
        }else if(data.attr.type=="link"){
            window.open(data.attr.url,"_blank")
        }else{
            window.setValue(data.attr.value, true)
        }
    }
</script>
<button class="main" class:select={data.attr.type=="toggle"&&$values[data.attr.value]} style={data.attr.style} on:click={click}>
    {data.text}{data.attr.type=="link"?" ":""}
    <slot />
</button>
<style lang="scss">
    $light: (
        Button-FillColor: #fefefe,
        Button-HoverColor: #fbfbfb,
        Button-ActiveColor: #fcfcfc,
        Button-BorderColor: #eeeeee,
    );
    $dark: (
        Button-FillColor: #3e3e3e,
        Button-HoverColor: #444444,
        Button-ActiveColor: #393939,
        Button-BorderColor: #454545,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .main{
        display: flex;
        font-size: 14px;
        background-color: var(--Button-FillColor);
        border-radius: 4px;
        padding: 6px 10px;
        box-shadow: 0 1px 0 0 #00000030, 0 0 0 1px var(--Button-BorderColor) inset;
        &:hover{
            background-color: var(--Button-HoverColor);
        }
        &:active{
            box-shadow: 0 0 0 1px var(--Button-BorderColor) inset;
            background-color: var(--Button-ActiveColor);
        }
        &.select{
            box-shadow: 0 1px 0 0 #00000030;
            color: var(--TextOnAccentFillColorPrimaryBrush);
            background-color: var(--AccentFillColorSecondaryBrush);
            &:hover{
                background-image: linear-gradient(var(--AccentHoverCoverColor));
            }
            &:active{
                background-image: linear-gradient(var(--AccentActiveCoverColor));
            }
        }
	}
</style>