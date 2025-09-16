<script lang="ts">
    import { values, format } from '../App.svelte';
    import Component from './Component.svelte';
    export let data: { [key: string]: any };

    const formatOption = (targetData) => {
        let isChange = targetData.tag == "Option";
        return {
            tag: targetData.tag,
            attr: { ...targetData.attr, ...(isChange ? { optionValue: data.attr.value } : {}) },
            text: targetData.text,
            child: targetData.child.map(formatOption)
        };
    };

    let open=false
    let main
</script>
<svelte:window on:click={(e)=>{if(!main?.contains(e.target))open=false}}></svelte:window>
<span class="container" class:disabled={Boolean(data.attr.disabled)} style="
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
">
    <button class="main" on:click={()=>{open=!open}} bind:this={main}>
        <p>
            {data.text?`${data.text}: `:''}{$values[`${data.attr.value}._Option`]}
        </p>
        <span></span>
    </button>
    <div class="menu" style="display: {open?'flex':'none'};">
        {#each data.child as child}
            {@const childData = formatOption({
                tag: child.tag,
                attr: Object.fromEntries(Object.entries(child.attr).map(([k, v]) => [k, format(v)])),
                text: format(child.text),
                child: child.child
            })}
                <Component formatData={childData} />
        {/each}
    </div>
</span>
<style lang="scss">
    $light: (
        Select-FillColor: #fefefe,
        Select-HoverColor: #fbfbfb,
        Select-ActiveColor: #fcfcfc,
        Select-BorderColor: #eeeeee,
        Select-MenuFillColor: #f9f9f9,
        Select-MenuBorderColor: #ededed,
    );
    $dark: (
        Select-FillColor: #3e3e3e,
        Select-HoverColor: #444444,
        Select-ActiveColor: #393939,
        Select-BorderColor: #454545,
        Select-MenuFillColor: #2c2c2c,
        Select-MenuBorderColor: #1f1f1f,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .main{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: space-between;
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
    }
</style>