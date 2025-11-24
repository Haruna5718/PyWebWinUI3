<script lang="ts">
    export let data: { [key: string]: any };
</script>
<div class="page" class:header={data.attr.title}>
    {#if data.attr.title}
        <p class="title">{data.attr.title}</p>
    {/if}
    <div class="content">
        <slot />
    </div>
</div>
<style lang="scss">
    .page{
        display: flex;
        flex-direction: column;
        border: 1.5px solid var(--CardStrokeColorDefaultSolidBrush);
		border-bottom: none;
		border-right: none;
		background-color: var(--SolidBackgroundFillColorQuarternaryBrush);
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
            align-items: center;
        }
    }
	@keyframes PageLoadAnim {
		0%{
			transform: translateY(50px);
		}
    }
</style>