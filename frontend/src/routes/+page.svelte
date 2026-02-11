<script context="module">
  	import { writable, get } from 'svelte/store';
	import '../lib/ThemeResources.scss';

	export const values = writable<Record<string, any>>({
		"system_goBack": true,
		"system_pinTop": true,
		"system_title": null,
		"system_icon": null,
		"system_theme": "system",
		"system_accent": ["#fff","#fff","#fff","#888","#000","#000","#000"],
		"system_pin": false,
		"system_pages": null,
		"system_settings": null,
		"system_nofication": []
	});

	export const format = (text:string) => {
		let v = get(values);

		const t = text.match(/^(?<!\\)\{([^}]+)\}$/);
		if(t) {
			if(v[t[1]]){
				return v[t[1]]
			}
			try {
				return Function('v', `with(v){ return ${t[1]} }`)(v);
			} catch(e) {
				return text;
			}
		}
		
		return text.replace(/(?<!\\){(.*?)}/g, (m, d) => {
			if(v[d[1]]){
				return v[d[1]]
			}
			try {
				return Function('v', `with(v){ return ${d} }`)(v);
			} catch(e) {
				return m;
			}
		}).replace(/\\({.*?})/g, "$1");
	};
</script>
<script lang="ts">
    import { onMount } from 'svelte';

	import Component from "../lib/Component.svelte";

	let isNavOpen = true;

    onMount(async () => {
        window.syncValue = (target:string, value:any, sync=true) => {
            if(!target) return;
            values.update(dict=>{
                return { ...dict, [target]: value };
            });
            if(target.endsWith("_Temp")) return;
            if(sync) window.pywebview.api.syncValue(target, value)
        }
        history.replaceState({i:0},"");
        hashChange();
        while (!window?.pywebview?.api?.hasOwnProperty("init")) await new Promise(resolve => setTimeout(resolve, 10));
        let appConfig = await window.pywebview.api.init();
        values.update(dict=>{
            return { ...dict, ...appConfig };
        });
    })

	let hash:string;
	let RecentPages = 0;
	const hashChange = () => {
		if(location.hash==`#${hash}`) return
		hash = location.hash.replace("#","")
		if(history.state==null) history.replaceState({i:RecentPages+1}, "");
		RecentPages = history.state.i;
	}
</script>
<svelte:window on:hashchange={hashChange}></svelte:window>
<main class={$values['system_theme']} style="
	grid-template-columns: {isNavOpen ? 230 : 50}px 1fr;
	{['Light3','Light2','Light1','','Dark1','Dark2','Dark3'].map((v,i)=>`--SystemAccentColor${v}:${$values['system_accent'][i]};`).join('')}
	--AccentFillColorLightSecondaryBrush: {$values['system_accent'][1]}E6;
	--AccentFillColorLightTertiaryBrush: {$values['system_accent'][1]}CC;
	--AccentFillColorDarkSecondaryBrush: {$values['system_accent'][4]}E6;
	--AccentFillColorDarkTertiaryBrush: {$values['system_accent'][4]}CC;
">
	<header>
		<div class="pywebview-drag-region"></div>
		{#if $values["system_goBack"]}
			<button class="prevButton" on:click={()=>history.back()} disabled={!RecentPages}>
				<span class="icon"></span>
			</button>
		{/if}
		<div class="title pywebview-drag-region">
			<img src={$values["system_icon"]} alt="" style="opacity: {$values["system_icon"]?1:0};"/>
			<p>{$values["system_title"]??""}</p>
		</div>
		{#if $values["system_pinTop"]}
			<button on:click={()=>window.pywebview.api.pin(!$values["system_pin"])}>{$values["system_pin"]?'':''}</button>
		{/if}
		<button on:click={()=>window.pywebview.api.minimize()}></button>
		<button on:click={()=>window.pywebview.api.destroy()}></button>
	</header>
	<nav style="grid-template-rows: 40px 1fr {$values['system_settings'] ? '40px': ''};">
		<button class="menuButton" style="width: 40px" on:click={()=>isNavOpen=!isNavOpen}>
			<span class="icon"></span>
		</button>
		<section>
			{#each Object.keys($values["system_pages"] ?? {}).sort() as key}
				{@const val = $values["system_pages"][key]}
				<button class:settingButton={val["attr"]?.["icon"]==""} class:Select={hash==key} on:click={()=>location.hash=key}>
					<span class="icon">{val["attr"]?.["icon"] ?? ""}</span>
					<span>{val["attr"]?.["name"] ?? key}</span>
					{#if format(val['attr']?.['state']??"")}
						<span class="badge l{format(val['attr']?.['state']??"")}">{format(val["attr"]?.["badge"]??"")??""}</span>
					{/if}
				</button>
			{/each}
		</section>
		{#if $values["system_settings"]}
			{@const path = $values["system_settings"]["attr"]?.["path"] ?? "settings"}
			{@const icon = $values["system_settings"]["attr"]?.["icon"] ?? ""}
			{@const state = $values["system_settings"]["attr"]?.["state"]}
			<button class:settingButton={icon==""} class:Select={hash==path} on:click={()=>location.hash=path}>
				<span class="icon">{icon}</span>
				<span>{$values["system_settings"]["attr"]?.["name"] ?? "Settings"}</span>
				{#if format(state??"")}
						<span class="badge l{format(state??"")}">{format($values["system_settings"]["attr"]?.["badge"]??"")??""}</span>
					{/if}
			</button>
		{/if}
	</nav>
	{#key hash}
		{#if $values["system_settings"]?.["attr"]?.["path"]==hash}
			<Component rawData={$values["system_settings"]}/>
		{:else if $values["system_pages"]?.[hash]}
			<Component rawData={$values["system_pages"][hash]}/>
		{:else if $values["system_pages"]==null}
			<div class="pageMessage">
				<p>Initializing...</p>
			</div>
		{:else}
			<div class="pageMessage">
				<h1>404 Not Found</h1>
				<p>The page '{hash}' does not exist.</p>
			</div>
		{/if}
	{/key}
	<div class="nofication" style="max-width: calc(100% - {isNavOpen ? 250 : 70}px);">
		{#each $values["system_nofication"] as [level,title,description,item], ind}
			<div class="InfoBar l{level}">
				<span class="icon">{["","","",""][level]}</span>
				<span class="content">
					<span class="title">{title}</span>
					<span class="description">{description}</span>
					{#if item}
						<span class="item">
							<Component rawData={item}/>
						</span>
					{/if}
				</span>
				<button class="close" on:click={()=>window.syncValue("system_nofication",$values["system_nofication"].filter((_:any, i:number)=>i!=ind))}></button>
			</div>
		{/each}
	</div>
</main>
<style lang="scss">
	.pageMessage{
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		p{
			color: var(--TextFillColorDisabledBrush);
		}
	}
	.nofication{
		display: flex;
		gap: 4px;
		position: absolute;
		flex-direction: column;
		align-items: flex-end;
		z-index: 1000;
		right: 10px;
		top: 60px;
		.InfoBar{
			width: fit-content;
			display: flex;
			gap: 10px;
			align-items: center;
			border-radius: 4px;
			padding: 6px;
			box-shadow: 0 0 4px 1px var(--SmokeFillColorDefaultBrush);
			&.l0{
				background-color: var(--SystemFillColorSolidAttentionBackgroundBrush);
				.icon{
					color: var(--SystemFillColorSolidAttentionBackgroundBrush);
					background-color: var(--SystemFillColorAttentionBrush);
				}
			}
			&.l1{
				background-color: var(--SystemFillColorSuccessBackgroundBrush);
				.icon{
					color: var(--SystemFillColorSuccessBackgroundBrush);
					background-color: var(--SystemFillColorSuccessBrush);
				}
			}
			&.l2{
				background-color: var(--SystemFillColorCautionBackgroundBrush);
				.icon{
					color: var(--SystemFillColorCautionBackgroundBrush);
					background-color: var(--SystemFillColorCautionBrush);
				}
			}
			&.l3{
				background-color: var(--SystemFillColorCriticalBackgroundBrush);
				.icon{
					color: var(--SystemFillColorCriticalBackgroundBrush);
					background-color: var(--SystemFillColorCriticalBrush);
				}
			}
			.icon{
				display: flex;
				align-items: center;
				align-self: flex-start;
				justify-content: center;
				font-size: 18px;
				padding: 0 0 0.5px 0.5px;
				margin: 9px 0 9px 9px;
				height: 16px;
				width: 16px;
				border-radius: 8px;
				color: var(--SystemFillColorCriticalBackgroundBrush);
				background-color: var(--SystemFillColorCriticalBrush);
			}
			.content{
				display: flex;
				gap: 0;
				flex-wrap: wrap;
				min-height: 34px;
				.item{
					display: flex;
					align-self: center;
				}
				.title{
					display: flex;
					margin: 6px 8px 0 0;
					line-height: 20px;
				}
				.description{
					display: flex;
					align-self: center;
					flex-grow: 1;
					font-size: 14px;
					font-variation-settings: 'wght' 400;
					word-wrap: break-word;
					overflow-wrap: anywhere;
					margin: 4px 8px 4px 0;
				}
			}
			.close{
				flex: 0 0 34px;
				height: 34px;
				border-radius: 4px;
				align-self: flex-start;
				&:hover{
					background-color: var(--SubtleFillColorSecondaryBrush);
				}
				&:active{
					background-color: var(--SubtleFillColorTertiaryBrush);
				}
			}
		}
	}
	.prevButton{
		width: 40px;
		height: 40px;
		margin: 0;
		color: var(--TextFillColorPrimaryBrush);
		
		display: flex;
		align-items: center;
		justify-content: center;
		&>.icon{
			animation : prevMove 0.2s forwards alternate;
			@keyframes prevMove {
				0%{
					transform: scaleX(0.8) translateX(12%);
				}
				80%{
					transform: scaleX(1.1) translateX(-6%);
				}
				100%{
					transform: scaleX(1) translateX(0);
				}
			}
		}
		&:active>.icon{
			animation: none;
			scale: 80% 100%;
			translate: 12% 0%;
		}
	}
	.settingButton{
		&>.icon{
			animation : settingRotate 0.6s forwards alternate;
			@keyframes settingRotate {
				0%{
					transform: rotate(0);
				}
				100%{
					transform: rotate(120deg);
				}
			}
		}
		&:active>.icon{
			animation: none;
			rotate: -60deg;
		}
	}
	.menuButton{
		&:active>.icon{
			transform: scaleX(0.5);
		}
	}
	main{
		display: grid;
		grid-template-rows: 50px 1fr;
		background-color: var(--SolidBackgroundFillColorBaseBrush);
		color: var(--TextFillColorPrimaryBrush);
		width: 100vw;
		height: 100vh;
	}
	header{
		user-select: none;
		grid-column: span 2;
		display: flex;
		font-size: 13px;
		align-items: center;
		padding: 5px;
		justify-content: space-between;
		.pywebview-drag-region:not(.title){
			position: absolute;
			inset: 0;
		}
		.title{
			gap: 8px;
			flex-grow: 1;
			display: flex;
			align-items: center;
			padding: 8px;
			img{
				width: 20px;
				height: 20px;
			}
		}
		button{
			color: var(--TextFillColorTertiaryBrush);
			width: 30px;
			height: 30px;
			font-size: 15px;
			margin: 5px;
			border-radius: 4px;
			&:hover{
				background-color: var(--SubtleFillColorSecondaryBrush);
				color: var(--TextFillColorSecondaryBrush);
			}
			&:active{
				background-color: var(--SubtleFillColorTertiaryBrush);
			}
			&:last-child:hover{
				background-color: var(--SystemFillColorCriticalBackgroundBrush);
				color: var(--SystemFillColorCriticalBrush);
			}
		}
	}
	nav{
		user-select: none;
		display: grid;
		padding: 5px 0px 5px 5px;
		gap: 5px;
		overflow: hidden;
		button{
			container-type: inline-size;
			display: flex;
			overflow: hidden;
			flex: 0 0 40px;
			gap: 1px;
			border-radius: 4px;
			margin-right: 5px;
			align-items: center;
			white-space: nowrap;
			.icon{
				flex: 0 0 40px;
				font-size: 16px;
			}
			.badge{
				position: absolute;
				right: 14px;
				line-height: 14px;
				font-size: 10px;
				padding: 0px 3px;
				min-width: 14px;
				min-height: 14px;
				border-radius: 8px;
				text-align: center;
				transition: all 0.2s ease-out, right 0s, top 0s;
				color: var(--TextOnAccentFillColorPrimaryBrush);
				&.l0{
					background-color: var(--SystemFillColorAttentionBrush);
				}
				&.l1{
					background-color: var(--SystemFillColorSuccessBrush);
				}
				&.l2{
					background-color: var(--SystemFillColorCautionBrush);
				}
				&.l3{
					background-color: var(--SystemFillColorCriticalBrush);
				}
				&.l4{
					background-color: var(--SystemFillColorSolidNeutral);
				}
			}
			@container (max-width: 50px) {
				.badge{
					top: 6px;
					right: 6px;
					font-size: 0;
					line-height: 0;
					min-width: 10px;
					min-height: 10px;
				}
			}
			&::before{
				position: absolute;
				content: "";
				border-radius: 1.5px;
				width: 3px;
				height: 6px;
			}
			&.Select:hover{
				background-color: var(--SubtleFillColorTertiaryBrush);
			}
			&.Select,&.Select:active,&:not(.Select):hover{
				background-color: var(--SubtleFillColorSecondaryBrush);
			}
			&:not(.Select):active{
				background-color: var(--SubtleFillColorTertiaryBrush);
			}
			&.Select::before{
				height: 16px;
				background-color: var(--AccentFillColorSecondaryBrush);
			}
		}
		section{
			display: flex;
			flex-direction: column;
			gap: 5px;
			overflow: hidden scroll;
			button{
				margin-right: 1px;
			}
		}
	}
</style>