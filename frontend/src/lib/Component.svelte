<script lang="ts">
	import { formatComponentSource } from '../routes/+page.svelte';

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
	import Option from './Option.svelte';
	import Match from './Match.svelte';

	type ComponentData = { [key: string]: any } | undefined;
	const Components: Record<string, any> = {
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
		Repeat,
		Option,
		Match
	};

	export let rawData: ComponentData = undefined; 
	export let formatData: ComponentData = undefined;

</script>
{#if rawData||formatData}
	{@const source = (formatData ?? rawData)!}
	{@const data = formatData ?? formatComponentSource(source)}
	{#if ["Select","Slider","Switch","Text","Line","Input","Progressbar","Button","Check","Radio","Webview","Image","If","Repeat","Option","Match","Expender"].includes(data.tag)}
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
