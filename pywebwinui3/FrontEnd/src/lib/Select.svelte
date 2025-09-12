<script lang="ts">
    import { values, format } from '../App.svelte';
    export let data: { [key: string]: any };

    let open=false
    let main
</script>
<svelte:window on:click={(e)=>{if(!main?.contains(e.target))open=false}}></svelte:window>
<span class="container" bind:this={main}>
    <button class="main" style={data.attr.style} on:click={()=>{open=!open}}>
        <p>
            {data.text?`${data.text}: `:''}{data.child.find(child=>child.attr.value==$values[data.attr.value])?.text}
        </p>
        <span></span>
    </button>
    {#if open}
        <div class="menu">
            {#each data.child as child}
                {@const childAttr = Object.fromEntries(Object.entries(child.attr).map(([k, v]) => [k, format(v)]))}
                <button class="item" style={childAttr.style} class:select={$values[data.attr.value]==child.attr.value} on:click={()=>{open=false;window.setValue(data.attr.value, childAttr.value)}}>
                    {format(child.text)}
                </button>
            {/each}
        </div>
    {/if}
</span>
<style lang="scss">
    $light: (
        Select-FillColor: #fefefe,
        Select-HoverColor: #fbfbfb,
        Select-ActiveColor: #fcfcfc,
        Select-BorderColor: #eeeeee,
        Select-MenuFillColor: #f9f9f9,
        Select-MenuHoverColor: #f0f0f0,
        Select-MenuActiveColor: #f3f3f3,
        Select-MenuBorderColor: #ededed,
    );
    $dark: (
        Select-FillColor: #3e3e3e,
        Select-HoverColor: #444444,
        Select-ActiveColor: #393939,
        Select-BorderColor: #454545,
        Select-MenuFillColor: #2c2c2c,
        Select-MenuHoverColor: #383838,
        Select-MenuActiveColor: #343434,
        Select-MenuBorderColor: #1f1f1f,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .main{
        display: flex;
        font-size: 14px;
        background-color: var(--Select-FillColor);
        border-radius: 4px;
        padding: 6px 10px;
        box-shadow: 0 1px 0 0 #00000030, 0 0 0 1px var(--Select-BorderColor) inset;
        &:hover{
            background-color: var(--Select-HoverColor);
        }
        &:active{
            box-shadow: 0 0 0 1px var(--Select-BorderColor) inset;
            background-color: var(--Select-ActiveColor);
            span{
                transform: translateY(2px);
            }
        }
        span{
            margin-left: 4px;
            display: flex;
            align-items: center;
        }
	}
    .menu{
        display: flex;
        flex-direction: column;
        animation : onAnim 0.2s ease-out forwards alternate;
        z-index: 100;
        padding: 4px;
        background-color: var(--Select-MenuFillColor);
        border: 1.5px solid var(--Select-MenuBorderColor);
        border-radius: 8px;
        position: absolute;
        left: 50%;
        translate: -50%;
        gap: 5px;
        width: max-content;
        box-shadow: 0 1px 1px 0 #00000030;
        @keyframes onAnim {
            0%{
                transform: translateY(0px);
            }
            100%{
                transform: translateY(10px);
            }
        }
        .item{
            text-align: left;
            align-self: stretch;
            border-radius: 4px;
            background-color: transparent;
            padding: 6px 12px;
            &.select,&.select:active,&:hover:not(:active){
				background-color: var(--Select-MenuHoverColor);
			}
            &.select:hover:not(:active),&:active{
                background-color: var(--Select-MenuActiveColor);
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
    }
</style>