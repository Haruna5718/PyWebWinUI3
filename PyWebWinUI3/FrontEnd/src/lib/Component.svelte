<script lang="ts">
    import { values, format } from '../App.svelte';

    import Component from './Component.svelte';
    
    import Page from './Page.svelte';
    import Text from './Text.svelte';
    import Line from './Line.svelte';
    import Space from './Space.svelte';
    import Box from './Box.svelte';
    import Vertical from './Vertical.svelte';
    import Horizontal from './Horizontal.svelte';
    import Button from './Button.svelte';
    import Input from './Input.svelte';
    import Switch from './Switch.svelte';
    import Select from './Select.svelte';
    import Slider from './Slider.svelte';
    import Check from './Check.svelte';
    import Progressbar from './Progressbar.svelte';
    import Expender from './Expender.svelte';
    import Radio from './Radio.svelte';
    import Image from './Image.svelte';
    import Webview from './Webview.svelte';
    import If from './If.svelte';
    import Repeat from './Repeat.svelte';

    // type layoutDataType = {
    //     tag: string,
    //     attr: {[key: string]: string},
    //     text: string,
    //     child: layoutDataType[];
    // };

    const Components = {
        Text,
        Line,
        Space,
        Box,
        Vertical,
        Horizontal,
        Button,
        Input,
        Switch,
        Select,
        Slider,
        Check,
        Page,
        Progressbar,
        Expender,
        Radio,
        Image,
        Webview,
        If,
        Repeat
    };

    // function SetRepeatData(data: layoutDataType, ind: number): layoutDataType {
    //     Object.keys(data.Attr).forEach((key)=>{
    //         data.Attr[key] = data.Attr[key].replaceAll(/\{i\}/g, `${ind}`);
    //     })
    //     data.Text = data.Text.replaceAll(/\{i\}/g, `${ind}`);
    //     data.Children = data.Children.map((child) => SetRepeatData(child, ind));
    //     return data;
    // }
    
    export let rawData: { [key: string]: any } = undefined; //:layoutDataType;
    export let formatData: { [key: string]: any } = undefined;

</script>
{#if rawData||formatData}
    {@const data = formatData??{
        tag: rawData.tag,
        attr: Object.fromEntries(Object.entries(rawData.attr).map(([k, v]) => [k, format(v)])),
        text: format(rawData.text),
        child: rawData.child
    }}
    {#if ["Select","Slider","Switch","Text","Line","Input","Progressbar","Button","Check","Radio","Webview","Image","If","Repeat"].includes(data.tag)}
        <svelte:component {data} this={Components[data.tag]} />
    {:else}
        <svelte:component {data} this={Components[data.tag]}>
            {#if data.text}
                <Text {data}/>
            {/if}
            {#each data.child as child}
                <Component rawData={child} />
            {/each}
        </svelte:component>
    {/if}
{/if}