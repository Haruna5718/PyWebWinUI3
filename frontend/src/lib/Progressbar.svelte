<script lang="ts">
    export let data: { [key: string]: any };
</script>
<span class="main {data.attr.type}" class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? '160px'};
    margin: {data.attr.margin ?? 0};
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