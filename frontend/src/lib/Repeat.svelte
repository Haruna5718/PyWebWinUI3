<script lang="ts">
    import Component from "./Component.svelte";
    export let data: { [key: string]: any };
    const formatIndex = (text:string, index:number) => {
        return text.replace(/(?<!\\){i}/g, () => index).replace(/\\({i})/g, "$1");
    };

    const formatIndexAll = (targetData:any, index:number) => {
        return {
            tag: targetData.tag,
            attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatIndex(v,index)])),
            text: formatIndex(targetData.text,index),
            child: targetData.child.map((child:any) => formatIndexAll(child,index))
        };
    };

    const formatVlaue = (text:string, value:any) => {
        return text.replace(/(?<!\\){(\d+)}/g, (m,k) => value[Number(k)]).replace(/\\({\d+})/g, "$1");
    };

    const formatVlaueAll = (targetData:any, value:any) => {
        return {
            tag: targetData.tag,
            attr: Object.fromEntries(Object.entries(targetData.attr).map(([k, v]) => [k, formatVlaue(v,value)])),
            text: formatVlaue(targetData.text,value),
            child: targetData.child.map((child:any) => formatVlaueAll(child,value))
        };
    };
</script>
{#if String(data.attr.disabled??"")!="true"}
    {#each new Array(Number(data.attr.data)||0) as _,index}
        {#each data.child as val}
            <Component rawData={formatIndexAll(val,index)}/>
        {/each}
    {/each}
{/if}