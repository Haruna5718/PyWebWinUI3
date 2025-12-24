<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };

    if ($values[data.attr.optionValue]==data.attr.value) window.syncValue(`${data.attr.optionValue}._Temp`, data.text);
</script>
<button class:select={$values[data.attr.optionValue]==data.attr.value} on:click={()=>{window.syncValue(data.attr.optionValue, data.attr.value);window.syncValue(`${data.attr.optionValue}._Temp`, data.text)}}>
    {data.text}
</button>
<style lang="scss">
    button{
        text-align: left;
        align-self: stretch;
        border-radius: 4px;
        background-color: transparent;
        padding: 6px 12px;
        &.select,&.select:active,&:hover:not(:active){
            background-color: var(--SubtleFillColorSecondaryBrush);
        }
        &.select:hover:not(:active),&:active{
            background-color: var(--SubtleFillColorTertiaryBrush);
        }
        &.select:active::before{
            height: 6px;
        }
        &.select::before{
            position: absolute;
            content: "";
            border-radius: 1.5px;
            left: 0;
            top: 50%;
            width: 3px;
            height: 16px;
            transform: translateY(-50%);
            background-color: var(--AccentFillColorDefaultBrush);
        }
    }
</style>