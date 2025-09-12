<script lang="ts">
    export let data: { [key: string]: any };
</script>
<div class="page" style={data.attr.style} class:header={data.attr.title}>
    {#if data.attr.title}
        <p class="title">{data.attr.title}</p>
    {/if}
    <div class="content">
        <slot />
    </div>
</div>
<style lang="scss">
    $light: (
        Page-FillColor: #f9f9f9,
        Page-BorderColor: #eaeaea,
    );
    $dark: (
        Page-FillColor: #272727,
        Page-BorderColor: #1d1d1d,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}

    .page{
        display: flex;
        flex-direction: column;
        border: 1.5px solid var(--Page-BorderColor);
		border-bottom: none;
		border-right: none;
		background-color: var(--Page-FillColor);
		border-top-left-radius: 8px;
        overflow: hidden;
        &.header{
            .content{
                padding-top: 4px;
            }
            .title{
                font-size: 24px;
                z-index: 10;
                position: sticky;
                background-color: inherit;
                padding: 28px 0 4px 36px;
                top: 0px;
                animation : PageLoadAnim 0.1s ease-out forwards alternate;
            }
        }
        .content{
            animation : PageLoadAnim 0.1s ease-out forwards alternate;
            overflow: hidden scroll;
            display: flex;
		    flex-direction: column;
            align-self: stretch;
            flex-grow: 1;
            gap: 4px;
            padding: 36px 32px 36px 36px;
        }
    }
	@keyframes PageLoadAnim {
		0%{
			transform: translateY(50px);
		}
    }
</style>