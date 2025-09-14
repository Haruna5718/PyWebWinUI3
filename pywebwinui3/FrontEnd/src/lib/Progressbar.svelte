<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
</script>
<span class="main {data.attr.type}" class:disabled={Boolean(data.attr.disabled)}>
    <span />
    <div style="width: {$values[data.attr.value]??0}%"/>
</span>
<style lang="scss">
    $light: (
        Progressbar-BackFillColor: #868686,
    );
    $dark: (
        Progressbar-BackFillColor: #9a9a9a,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .main{
        align-self: center;
        height: 4px;
        width: 160px;
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
            background-color: var(--AccentFillColorSecondaryBrush);
            box-shadow: 0 1px 0 0 #00000030;
        }
        &.progress{
            span{
                background-color: var(--Progressbar-BackFillColor);
                box-shadow: 0 1px 0 0 #00000030;
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