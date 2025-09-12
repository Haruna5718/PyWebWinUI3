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
            {data.child.find(child=>child.attr.value==$values[data.attr.value])?.text}
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
    .main{
        display: flex;
        font-size: 14px;
        background-color: var(--ButtonFillColor);
        border-radius: 4px;
        padding: 6px 10px;
        box-shadow: 0 0 0 1px var(--ButtonBorderColor) inset;
        &:hover{
            background-image: linear-gradient(var(--ButtonHoverColor));
        }
        &:active{
            background-image: linear-gradient(var(--ButtonActiveColor));
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
        border: 1.5px solid var(--SelectMenuBorderColor);;
        background-color: var(--SelectMenuFillColor);
        border-radius: 8px;
        position: absolute;
        left: 50%;
        translate: -50%;
        gap: 5px;
        width: max-content;
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
            &.select,&:hover{
				background-color: var(--NavButtonActiveColor);
			}
            &:active{
                background-color: var(--NavButtonHoverColor);
                &.select::before{
                    height: 6px;
                }
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