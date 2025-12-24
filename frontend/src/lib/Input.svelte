<script lang="ts">
    import { values } from '../routes/+page.svelte';
    export let data: { [key: string]: any };
    let ispasswordShow = false
    let padding:number
</script>
<span class:disabled={String(data.attr.disabled??"")=="true"} style="
    margin: {data.attr.margin ?? 0};
    width: {data.attr.width ?? 'auto'};
    height: {data.attr.height ?? 'auto'};
">
    <input
        type={data.attr.type=="password"?(ispasswordShow?"text":"password"):data.attr.type}
        placeholder={data.text}
        on:input={(e)=>{window.syncValue(data.attr.value, data.attr.type=="number"?Number(e.currentTarget.value):e.currentTarget.value)}}
        min={data.attr.min}
        max={data.attr.max}
        value={$values[data.attr.value]}
        style="padding-right: {(padding??10)-2}px;"
    />
    {#if data.attr.type=="number"}
        <span class="buttons" bind:clientWidth={padding}>
            <button on:click={()=>window.syncValue(data.attr.value, Number($values[data.attr.value])+1)}></button>
            <button on:click={()=>window.syncValue(data.attr.value, Number($values[data.attr.value])-1)}></button>
        </span>
    {/if}
    {#if data.attr.type=="password"}
        <span class="buttons" bind:clientWidth={padding}>
            <button on:click={()=>ispasswordShow=!ispasswordShow}>{ispasswordShow?"":""}</button>
        </span>
    {/if}
</span>
<style lang="scss">
    .buttons{
        top: 0;
        right: 0;
        padding: 5px;
        align-self: center;
        position: absolute;
        height: 100%;
        display: flex;
        gap: 5px;
        button{
            width: 25px;
            border-radius: 4px;
            color: var(--ControlStrongFillColorDefaultBrush);
            &:hover{
                background-color: var(--SubtleFillColorSecondaryBrush);
            }
            &:active{
                background-color: var(--SubtleFillColorTertiaryBrush);
            }
        }
    }
    input{
        resize: none;
        height: fit-content;
        padding: 9px 8px 9px 8px;
        border-radius: 4px;
        background-color: var(--ControlFillColorDefaultBrush);
		border: 1px solid var(--ControlStrokeColorDefaultBrush);
        border-bottom: 1.5px solid var(--ControlStrongFillColorDefaultBrush);
        line-height: 1.3em;
        transition: all 0.1s ease-out, padding 0s, border-bottom-width 0s;
        width: 100%;
        height: 100%;
		&::-webkit-inner-spin-button,&::-webkit-outer-spin-button{
			appearance: none;
			margin: 0;
		}
        &::placeholder {
            color: var(--ControlStrongFillColorDefaultBrush);
            opacity: 1;
        }
        &:hover:not(:focus){
            background-color: var(--ControlFillColorSecondaryBrush);
        }
        &:focus{
            background-color: var(--ControlFillColorInputActiveBrush);
            padding: 9px 8px 8px 8px;
            border-bottom-width: 2.5px;
            border-bottom-color: var(--AccentFillColorDefaultBrush);
        }
    }
</style>