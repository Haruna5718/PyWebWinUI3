<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
    let open=false
    $: Header = data.child.find((d:any)=>"Header"==d.tag)

    function toggle(event?: MouseEvent | KeyboardEvent) {
        if (String(data.attr.disabled ?? "") == "true") {
            return;
        }
        if (event && "target" in event) {
            const target = event.target as HTMLElement | null;
            const currentTarget = event.currentTarget as HTMLElement | null;
            const interactive = target?.closest(
                "button, a, input, select, textarea, summary, [role='button'], [contenteditable='true']"
            );
            if (interactive && interactive !== currentTarget) {
                return;
            }
        }
        open = !open;
    }

    function onKeydown(event: KeyboardEvent) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            toggle(event);
        }
    }
</script>
<div class="main" style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
    border-radius: {data.attr.round ?? '4px'};
">
    <div
        class="button"
        class:open={open}
        class:disabled={String(data.attr.disabled??"")=="true"}
        role="button"
        tabindex={String(data.attr.disabled??"")=="true" ? -1 : 0}
        aria-expanded={open}
        on:click={toggle}
        on:keydown={onKeydown}
    >
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
    </div>
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
        
        .button{
            align-items: inherit;
            display: flex;
            flex-grow: 1;
            align-self: stretch;
            flex-direction: row;
            border-radius: inherit;
            cursor: pointer;
            
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
            &:focus-visible{
                outline: 2px solid var(--AccentFillColorDefaultBrush);
                outline-offset: -2px;
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
            &.disabled{
                cursor: default;
                pointer-events: none;
                opacity: 0.7;
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
