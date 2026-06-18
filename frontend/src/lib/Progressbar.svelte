<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span class="main {data.attr.type}" class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? '160px'};
    height: {data.attr.height ?? '4px'};
    --progress-round: {data.attr.round ?? '2px'};
    --progress-track-round: {data.attr.trackRound ?? '1px'};
    --progress-color: {data.attr.color ?? 'var(--AccentFillColorDefaultBrush)'};
    --progress-background: {data.attr.background ?? 'var(--ControlStrongFillColorDefaultBrush)'};
    --progress-shadow: {data.attr.shadow ?? '0 1px 0 0 var(--SmokeFillColorDefaultBrush)'};
">
    <span> </span>
    <div style="width: {data.attr.data??0}%"></div>
</span>
<style lang="scss">
    @keyframes running {
        0%{
            transform: translateX(-100%);
        }
        100%{
            transform: translateX(200%);
        }
    }
    .main{
        align-self: center;
        height: 100%;
        border-radius: var(--progress-round);
        overflow: hidden;
        span{
            position: absolute;
            inset: 1px;
            border-radius: var(--progress-track-round);
        }
        div{
            position: absolute;
            inset: 0;
            border-radius: var(--progress-round);
            background-color: var(--progress-color);
            box-shadow: var(--progress-shadow);
        }
        &.progress{
            span{
                background-color: var(--progress-background);
                box-shadow: var(--progress-shadow);
            }

        }
        &.running{
            div{
                width: 50% !important;
                animation : running 1s infinite ease-in-out forwards;
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
