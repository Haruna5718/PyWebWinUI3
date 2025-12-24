<script lang="ts">
    import { values, format } from '../routes/+page.svelte';
    import Component from './Component.svelte';
    export let data: { [key: string]: any };

    const formatOption = (targetData:any) => {
        let isChange = targetData.tag == "Option";
        return {
            tag: targetData.tag,
            attr: { ...targetData.attr, ...(isChange ? { optionValue: data.attr.value } : {}) },
            text: targetData.text,
            child: targetData.child.map(formatOption)
        };
    };

    let open=false
    let main:HTMLButtonElement
</script>
<svelte:window on:click={(e)=>{if(!main?.contains(e.target))open=false}}></svelte:window>
<span class="container" class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
">
    <button class="main" on:click={()=>{open=!open}} bind:this={main}>
        <p>
            {data.text?`${data.text}: `:''}{$values[`${data.attr.value}._Temp`]}
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
    @keyframes onAnim {
        0%{
            transform: translateY(0px);
        }
        100%{
            transform: translateY(10px);
        }
    }
    .main{
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        background-color: var(--ControlFillColorDefaultBrush);
        border-radius: 4px;
        padding: 6px 10px;
        box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
        &:hover{
            background-color: var(--ControlFillColorSecondaryBrush);
        }
        &:active{
            box-shadow: 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
            background-color: var(--ControlFillColorTertiaryBrush);
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
        background-color: var(--SolidBackgroundFillColorQuarternaryBrush);
        border: 1.5px solid var(--SurfaceStrokeColorFlyoutBrush);
        border-radius: 8px;
        position: absolute;
        left: 50%;
        translate: -50%;
        gap: 5px;
        width: max-content;
        box-shadow: 0 1px 1px 0 var(--SmokeFillColorDefaultBrush);
    }
</style>