<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
    let width,height;
    $: min = +data?.attr?.min || 0;
    $: max = +data?.attr?.max || 100;
    $: step = +data?.attr?.step || 1;

    $: value = Math.min(Math.max(+$values?.[data?.attr?.value] || 0, min), max);

    $: percent = (1 - ((max - value) / (max - min)));
    let click = false;
</script>
<span class="container" bind:clientWidth={width} bind:clientHeight={height} class:vertical={data.attr.type=="vertical"} class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    {data.attr.type=='vertical'?'height':'width'}: {data.attr.width ?? '160px'};
">
    <span class="main" style="width: {data.attr.type=='vertical'?height:width}px; right: {(data.attr.type=='vertical'?height-24:0)/2}px" bind:clientWidth={width}>
        <span style="width: calc({percent*100}% {percent>0.5?'-':'+'} {Math.abs(0.5-percent)*18}px);">
            {#if click}
                <div class="rotater">
                    <div>{value}</div>
                </div>
            {/if}
        </span>
        <input type="range" min={min} max={max} step={step} value={value} on:mousedown={()=>{click=true}} on:mouseup={()=>{click=false}} on:input={(e)=>window.syncValue(data.attr.value, e.currentTarget.value)}/>
    </span>
</span>
<style lang="scss">
    .container{
        transition: none;
        display: flex;
        &:not(.vertical){
            height: 24px;
        }
        &.vertical{
            width: 24px;
            .main{
                rotate: -90deg;
                span{
                    .rotater{
                        transform: translateX(50%) rotate(90deg);
                        div{
                            left: 45px;
                            transform: translateX(50%);
                        }
                    }
                }
            }
        }
        .main{
            transition: none;
            align-self: center;
            background-color: var(--ControlStrongFillColorDefaultBrush);
            box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
            height: 4px;
            border-radius: 2px;
            span{
                transition: all 0.1s ease-out, width 0s;
                border-radius: 2px;
                position: absolute;
                inset: 0;
                background-color: var(--AccentFillColorDefaultBrush);
                .rotater{
                    position: absolute;
                    z-index: 200;
                    transform: translateX(50%);
                    right: 0;
                    top: -40px;
                    div{
                        border: 1.5px solid var(--SurfaceStrokeColorFlyoutBrush);
                        background-color: var(--SolidBackgroundFillColorQuarternaryBrush);
                        border-radius: 4px;
                        padding: 2px 6px;
                        font-size: 14px;
                        box-shadow: 0 1px 1px 0 var(--SmokeFillColorDefaultBrush);
                    }
                }
            }
            input{
                width: inherit;
                top: -7px;
                appearance: none;
                &::-webkit-slider-runnable-track {
                    cursor: pointer;
                }
                &::-webkit-slider-thumb {
                    cursor: pointer;
                    appearance: none;
                    transition: all 0.1s ease-in-out;
                    border: 5px solid var(--ControlSolidFillColorDefaultBrush);
                    box-shadow: 0 1px 0 1px var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlSolidFillColorDefaultBrush);
                    background-color: var(--AccentFillColorDefaultBrush);
                    width: 18px;
                    height: 18px;
                    border-radius: 10px;
                    &:hover{
                        border-width: 3px;
                    }
                    &:active{
                        border-width: 6px;
                    }
                }
            }
        }
    }
</style>