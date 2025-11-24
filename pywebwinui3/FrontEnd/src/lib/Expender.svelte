<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
    let open=false
</script>
<div class="main" style="
    border-radius: {data.attr.round ?? '4px'};
">
    <button on:click={()=>{open=!open}} class:open={open} disabled={String(data.attr.disabled??"")=="true"}>
        <span class="header" style="
            gap: {data.attr.gap ?? 'inherit'};
            padding: {data.attr.padding ?? '16px'};
            align-items: {data.attr.align?.replace('right','flex-end')?.replace('left','flex-start') ?? 'inherit'};
        ">
            {#each data.child.find((d)=>"Header"==d.tag)?.child ?? [] as val}
            <Component rawData={val}/>
            {/each}
        </span>
        <span class="arrow"></span>
    </button>
    {#if open}
        <div class="content">
            {#each data.child.filter((d)=>"Content"==d.tag) ?? [] as val}
                {@const childData = {
                    tag: "Box",
                    attr: {...val.attr,round:"0",border:"0",gap:"4px"},
                    text: val.text,
                    child: val.child
                }}
                <Component rawData={childData}/>
            {/each}
        </div>
    {/if}
</div>
<style lang="scss">
    $light: (
        Expender-HoverColor: #F9F9F9,
        Expender-ActiveColor: #F9F9F9,
        Expender-ActiveBorderColor: #D1D1D1,
    );
    $dark: (
        Expender-HoverColor: #3A3A3A,
        Expender-ActiveColor: #2E2E2E,
        Expender-ActiveBorderColor: #373737,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}
    .main{
        display: flex;
        align-self: stretch;
        flex-direction: column;

        gap: 0;

        button{
            display: flex;
            flex-grow: 1;
            align-self: stretch;
            flex-direction: row;
            border-radius: inherit;
            
            border: 1.5px solid var(--Box-BorderColor);
            background-color: var(--Box-FillColor);
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
                background-color: var(--Expender-HoverColor);
                border-color: transparent;
            }
            &:active{
                background-color: var(--Expender-ActiveColor);
                border-color: var(--Expender-ActiveBorderColor);
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
            overflow: hidden;
            gap: 1px;
            display: flex;
            align-self: stretch;
            flex-direction: column;
            border: 1.5px solid var(--Box-BorderColor);
            border-top: none;
            border-radius: inherit;
            border-top-left-radius: 0;
            border-top-right-radius: 0;
            background-color: var(--Box-BorderColor);
        }
    }
</style>