<script lang="ts">
    export let data: { [key: string]: any };
</script>
<div style="
    gap: {data.attr.gap ?? 'inherit'};
    border-radius: {data.attr.round ?? '4px'};
    border-width: {data.attr.border ?? '1.5px'};
    padding: {data.attr.padding ?? '16px'};
    background-color: {data.attr.background ?? 'var(--Box-FillColor)'};
    align-items: {data.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
">
    <slot />
</div>
<style lang="scss">
    $light: (
        Box-FillColor: #fdfdfd,
        Box-BorderColor: #eaeaea,
    );
    $dark: (
        Box-FillColor: #323232,
        Box-BorderColor: #232323,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    div{
        display: flex;
        align-items: center;
        flex-direction: column;
        align-self: stretch;

        border-color: var(--Box-BorderColor);
        border-style: solid;
    }
</style>