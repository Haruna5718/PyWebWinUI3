<script lang="ts">
    import { values } from '../App.svelte';
    export let data: { [key: string]: any };
    const click = () => {
        if(data.attr.type=="toggle"){
            window.setValue(data.attr.value, !$values[data.attr.value])
        }else{
            if(data.attr.type=="link"&&data.attr.url) window.open(data.attr.url,`_${data.attr.target??'blank'}`)
            window.setValue(data.attr.value, true)
        }
    }
</script>
<button class="main" class:select={data.attr.type=="toggle"&&$values[data.attr.value]} disabled={String(data.attr.disabled??"")=="true"} on:click={click} style="
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
">
    {data.text}{data.attr.type=="link"?" ":""}
    <slot />
</button>
<style lang="scss">
    .main{
        display: flex;
        font-size: 14px;
        background-color: var(--ControlFillColorDefaultBrush);
        border-radius: 4px;
        padding: 6px 10px;
        box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush), 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
        &:hover{
            background-color: var(--ControlFillColorSecondaryBrush);
        }
        &:active{
            box-shadow: 0 0 0 1px var(--ControlStrokeColorDefaultBrush) inset;
            background-color: var(--ControlFillColorTertiaryBrush);
        }
        &.select{
            box-shadow: 0 1px 0 0 var(--SmokeFillColorDefaultBrush);
            color: var(--TextOnAccentFillColorPrimaryBrush);
            background-color: var(--AccentFillColorDefaultBrush);
            &:hover{
                background-color: var(--AccentFillColorSecondaryBrush);
            }
            &:active{
                background-color: var(--AccentFillColorTertiaryBrush);
                color: var(--TextOnAccentFillColorSecondaryBrush);
            }
        }
	}
</style>