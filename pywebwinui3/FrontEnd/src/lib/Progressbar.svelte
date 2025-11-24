<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span class="main {data.attr.type}" class:disabled={String(data.attr.disabled??"")=="true"} style="
    width: {data.attr.width ?? '160px'};
">
    <span />
    <div style="width: {$values[data.attr.value]??0}%"/>
</span>
<style lang="scss">
    .main{
        align-self: center;
        height: 4px;
        border-radius: 2px;
        overflow: hidden;
        span{
            position: absolute;
            inset: 1px;
            border-radius: 1px;
        }
        div{
            position: absolute;
            inset: 0;
            border-radius: 2px;
            background-color: var(--AccentFillColorDefaultBrush);
            box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
        }
        &.progress{
            span{
                background-color: var(--ControlStrongFillColorDefaultBrush);
                box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
            }

        }
        &.running{
            div{
                width: 50% !important;
                animation : running 1s infinite ease-in-out forwards;
            }
            @keyframes running {
                0%{
                    transform: translateX(-100%);
                }
                100%{
                    transform: translateX(200%);
                }
            }
        }
        &.success{
            div{
                width: 100% !important;
                background-color: var(--SystemFillColorSuccessBrush);
            }
        }
        &.paused{
            div{
                width: 100% !important;
                background-color: var(--SystemFillColorCautionBrush);
            }
        }
        &.error{
            div{
                width: 100% !important;
                background-color: var(--SystemFillColorCriticalBrush);
            }
        }
    }
</style>