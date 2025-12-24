<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
    let open=false
    $: Header = data.child.find((d:any)=>"Header"==d.tag)
</script>
<div class="main" style="
    border-radius: {data.attr.round ?? '4px'};
">
    <button on:click={()=>{open=!open}} class:open={open} disabled={String(data.attr.disabled??"")=="true"}>
        <span class="header" style="
            gap: {Header?.attr?.gap ?? '4px'};
            padding: {Header?.attr?.padding ?? '16px'};
            align-items: {Header?.attr?.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
        ">
            {#each Header?.child ?? [] as val}
                <Component rawData={val}/>
            {/each}
        </span>
        <span class="arrow"></span>
    </button>
    {#if open}
        {#each data.child.filter((d:any)=>"Content"==d.tag) ?? [] as child}
            <div class="content" style="
                gap: {child.attr.gap ?? '4px'};
                padding: {child.attr.padding ?? '16px'};
                align-items: {child.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
            ">
                {#each child.child ?? [] as val}
                    <Component rawData={val}/>
                {/each}
            </div>
        {/each}
    {/if}
</div>
<style lang="scss">
    .main{
        display: flex;
        align-self: stretch;
        align-items: center;
        flex-direction: column;
        
        gap: 0;
        
        button{
            align-items: inherit;
            display: flex;
            flex-grow: 1;
            align-self: stretch;
            flex-direction: row;
            border-radius: inherit;
            
            border: 1px solid var(--CardStrokeColorDefaultSolidBrush);
            background-color: var(--CardBackgroundFillColorDefaultBrush);
            span{
                display: flex;
                &.header{
                    flex-wrap: wrap;
                    align-self: stretch;
                    flex-direction: column;
                    flex-grow: 1;
                }
                &.arrow{
                    align-self: center;
                    margin: 16px 16px 16px 0;
                }
            }
            &:hover{
                background-color: var(--ControlFillColorSecondaryBrush);
                border-color: var(--ControlStrokeColorDefaultBrush);
            }
            &:active{
                background-color: var(--CardBackgroundTertiaryBrush);
                border-color: var(--ControlStrokeColorDefaultBrush);
                .arrow{
                    transform: translateY(-1px);
                }
            }
            &.open{
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
                .arrow{
                    rotate: 180deg;
                }
            }
        }
        .content{
            display: flex;
            align-self: stretch;
            flex-direction: column;
            border: 1px solid var(--CardStrokeColorDefaultSolidBrush);
            border-top: none;
            border-radius: inherit;
            background-color: var(--CardBackgroundFillColorDefaultBrush);
            border-top-left-radius: 0;
            border-top-right-radius: 0;
            &:not(:last-child){
                border-radius: 0;
            }
        }
    }
</style>