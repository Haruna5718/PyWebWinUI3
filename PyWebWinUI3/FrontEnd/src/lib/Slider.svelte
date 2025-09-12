<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    let min,max,step,value,percent;
    $:{
        min=Number(data.attr.min ?? 0)
        max=Number(data.attr.max ?? 100)
        step=Number(data.attr.step ?? 1)
        value=Math.max(Math.min(Number($values[data.attr.value]??0),max),min)
        percent=(1-((max-value)/(max-min)))
    }
    let click = false;
</script>
<span class="container" class:vertical={data.attr.type=="vertical"}>
    <span class="main">
        <span style="width: calc({percent*100}% {percent>0.5?'-':'+'} {Math.abs(0.5-percent)*18}px);">
            {#if click}
                <div class="rotater">
                    <div>{value}</div>
                </div>
            {/if}
        </span>
        <input type="range" min={min} max={max} step={step} value={value} on:mousedown={()=>{click=true}} on:mouseup={()=>{click=false}} on:input={(e)=>window.setValue(data.attr.value, e.currentTarget.value)}/>
    </span>
</span>
<style lang="scss">
    $light: (
        Slider-BackFillColor: #868686,
        Slider-MenuFillColor: #f9f9f9,
        Slider-MenuBorderColor: #ededed,
        Slider-ThumbOuterColor: #ffffff,
        Slider-ThumbBorderColor: #00000020,
    );
    $dark: (
        Slider-BackFillColor: #9a9a9a,
        Slider-MenuFillColor: #2c2c2c,
        Slider-MenuBorderColor: #1f1f1f,
        Slider-ThumbOuterColor: #454545,
        Slider-ThumbBorderColor: #ffffff20,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .container{
        display: flex;
        &.vertical{
            height: 160px;
            width: 20px;
            .main{
                top: 0.5px;
                right: calc(300% + 9.5px);
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
            align-self: center;
            background-color: var(--Slider-BackFillColor);
            box-shadow: 0 1px 0 0 #00000030;
            height: 4px;
            width: 160px;
            border-radius: 2px;
            span{
                transition: all 0.1s ease-out, width 0s;
                border-radius: 2px;
                position: absolute;
                inset: 0;
                background-color: var(--AccentFillColorSecondaryBrush);
                .rotater{
                    position: absolute;
                    z-index: 200;
                    transform: translateX(50%);
                    right: 0;
                    top: -40px;
                    div{
                        border: 1.5px solid var(--Slider-MenuBorderColor);
                        background-color: var(--Slider-MenuFillColor);
                        border-radius: 4px;
                        padding: 2px 6px;
                        font-size: 14px;
                        box-shadow: 0 1px 1px 0 #00000030;
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
                    border: 5px solid var(--Slider-ThumbOuterColor);
                    box-shadow: 0 1px 0 1px #00000030, 0 0 0 1px var(--Slider-ThumbBorderColor);
                    background-color: var(--AccentFillColorSecondaryBrush);
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