<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span>
    <input
        type={data.attr.type}
        placeholder={data.text}
        on:input={(e)=>{window.setValue(data.attr.value, e.currentTarget.value)}}
        value={$values[data.attr.value]}
        style={data.attr.style}/>
    {#if data.attr.type=="number"}
        <span class="buttons">
            <button on:click={()=>window.setValue(data.attr.value, Number($values[data.attr.value])+1)}></button>
            <button on:click={()=>window.setValue(data.attr.value, Number($values[data.attr.value])-1)}></button>
        </span>
    {/if}
</span>
<style lang="scss">
    $light: (
        Input-FillColor: #fefefe,
        Input-HoverColor: #fbfbfb,
        Input-FocusColor: #ffffff,
        Input-BorderColor: #eeeeee,
		Input-BorderFocusColor: #616161,
        Input-InnerButtonHoverColor: #eaeaea,
		Input-InnerButtonActiveColor: #ededed,
    );
    $dark: (
        Input-FillColor: #3e3e3e,
        Input-HoverColor: #444444,
        Input-FocusColor: #242424,
        Input-BorderColor: #454545,
        Input-BorderFocusColor: #afafaf,
        Input-InnerButtonHoverColor: #ffffff0e,
		Input-InnerButtonActiveColor: #ffffff0a,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}
    .buttons{
        top: 0;
        right: 0;
        padding: 5px;
        align-self: center;
        position: absolute;
        height: 100%;
        display: flex;
        gap: 5px;
        button{
            width: 25px;
            border-radius: 4px;
            color: var(--Input-BorderFocusColor);
            &:hover{
                background-color: var(--Input-InnerButtonHoverColor);
            }
            &:active{
                background-color: var(--Input-InnerButtonActiveColor);
            }
        }
    }
    input{
        resize: none;

        width: 160px;
        height: fit-content;
        padding: 5px 6px 6px 6px;
        border-radius: 4px;
        background-color: var(--Input-FillColor);
		border: 1.5px solid var(--Input-BorderColor);
        border-bottom: 1.5px solid var(--Input-BorderFocusColor);
        line-height: 1.3em;
        box-shadow: 0 1px 0 0 #00000030;
        transition: all 0.1s ease-out, padding 0s, border-bottom-width 0s;
		&::-webkit-inner-spin-button,&::-webkit-outer-spin-button{
			appearance: none;
			margin: 0;
		}
        &::placeholder {
            color: var(--Input-BorderFocusColor);
            opacity: 1;
        }
        &:hover:not(:focus){
            background-image: linear-gradient(var(--Input-HoverColor));
        }
        &:active{
            box-shadow: none;
        }
        &:focus{
            background-color: var(--Input-FocusColor);
            padding: 5px 6px 5px 6px;
            border-bottom-width: 2.5px;
            border-bottom-color: var(--AccentFillColorSecondaryBrush);
        }
        &[type=number]{
            padding-right: 65px;
        }
    }
</style>