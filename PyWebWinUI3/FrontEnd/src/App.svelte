<script context="module">
  	import { writable, get } from 'svelte/store';

	export const values = writable({
		"system.goBack": true,
		"system.pinTop": true,
		"system.title": "PyWebWinUI3",
		"system.icon": "./favicon.ico",
		"system.theme": "dark",
		"system.color": ["#fff","#fff","#fff","#888","#000","#000","#000"],
		"system.isOnTop": false,
		"system.pages": null,
		"system.settings": null,
		"system.nofication": []
	});

	export const format = (text) => {
		const v = get(values);
        return text.replace(/(?<!\\){(.*?)}/g, (m, k) => v[k] ?? m).replace(/\\({.*?})/g, "$1");
    };
</script>
<script lang="ts">
	import Component from "./lib/Component.svelte";

	let isNavOpen = true;

	window.setValue = (target:string, value:any, sync=true) => {
		values.update(dict=>{
			return { ...dict, [target]: value };
		});
		if(sync) window.pywebview.api.setValue(target, value, false)
	}
	
	let hash = location.hash
	let RecentPages = 0;
	history.replaceState({i:0},"");
	const hashChange = () => {
		if(location.hash==`#${hash}`) return
		hash = location.hash.replace("#","")
		if(history.state==null) history.replaceState({i:RecentPages+1}, "");
		RecentPages = history.state.i;
	}
	hashChange();
	(async () => {
		while (!window.hasOwnProperty("pywebview")) await new Promise(resolve => setTimeout(resolve, 100));
		let appConfig = await window.pywebview.api.init()
		values.update(dict=>{
			return { ...dict, ...appConfig };
		});
	})();
	let currentTheme
	$:currentTheme = [0,1,$values['system.theme']][Number($values['settings.theme'])]
</script>
<svelte:window on:hashchange={hashChange}></svelte:window>
<main class={$values['system.theme']} style="
	grid-template-columns: {isNavOpen ? 230 : 50}px 1fr;
	{['Light3','Light2','Light1','Dark1','Dark2','Dark3'].map((v,i)=>`--SystemAccentColor${v}:${$values['system.color'][i]};`).join('')}
">
	<header>
		<div class="pywebview-drag-region"></div>
		{#if $values["system.goBack"]}
			<button class="prevButton" style="width: 40px; height: 40px; margin: 0; color: var(--TextFillColorPrimaryBrush);" on:click={()=>history.back()} disabled={!RecentPages}>
				<span class="icon"></span>
			</button>
		{/if}
		<div class="title pywebview-drag-region">
			<img src={$values["system.icon"]} alt="">
			<p>{$values["system.title"]}</p>
		</div>
		{#if $values["system.pinTop"]}
			<button on:click={()=>window.pywebview.api.ontop(!$values["system.isOnTop"])}>{#if $values["system.isOnTop"]}<span style="position:absolute;left:8px;"></span>{/if}</button>
		{/if}
		<button on:click={()=>window.pywebview.api.minimize()}></button>
		<button on:click={()=>window.pywebview.api.destroy()}></button>
	</header>
	<nav style="grid-template-rows: 40px 1fr {$values['system.settings'] ? '40px': ''};">
		<button class="menuButton" style="width: 40px" on:click={()=>isNavOpen=!isNavOpen}>
			<span class="icon"></span>
		</button>
		<section>
			{#each Object.entries($values["system.pages"] ?? {}) as val}
				<button class:settingButton={val[1]["attr"]?.["icon"]==""} class:Select={hash==val[0]} on:click={()=>location.hash=val[0]}>
					<span class="icon">{val[1]["attr"]?.["icon"] ?? ""}</span>
					<span>{val[1]["attr"]?.["name"] ?? val[0]}</span>
					{#if format(val[1]['attr']?.['state']??"")}
						<span class="badge l{format(val[1]['attr']?.['state']??"")}">{format(val[1]["attr"]?.["badge"]??"")??""}</span>
					{/if}
				</button>
			{/each}
		</section>
		{#if $values["system.settings"]}
			{@const path = $values["system.settings"]["attr"]?.["path"] ?? "settings"}
			{@const icon = $values["system.settings"]["attr"]?.["icon"] ?? ""}
			{@const badge = $values["system.settings"]["attr"]?.["badge"]}
			<button class:settingButton={icon==""} class:Select={hash==path} on:click={()=>location.hash=path}>
				<span class="icon">{icon}</span>
				<span>{$values["system.settings"]["attr"]?.["name"] ?? "Settings"}</span>
				{#if badge}
					<span class="badge">{format(badge)??""}</span>
				{/if}
			</button>
		{/if}
	</nav>
	{#key hash}
		{#if $values["system.settings"]?.["attr"]?.["path"]==hash}
			<Component rawData={$values["system.settings"]}/>
		{:else if $values["system.pages"]?.[hash]}
			<Component rawData={$values["system.pages"][hash]}/>
		<!-- {:else}
			<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
				<h1>404 Not Found</h1>
				<p>The page '{hash}' does not exist.</p>
			</div> -->
		{/if}
	{/key}
	<div class="nofication" style="max-width: calc(100% - {isNavOpen ? 250 : 70}px);">
		{#each $values["system.nofication"] as [level,title,description], ind}
			<div class="InfoBar l{level}">
				<span class="icon">{["","","",""][level]}</span>
				<span class="content">
					<span class="title">{title}</span>
					<span class="description">{description}</span>
				</span>
				<button class="close" on:click={()=>window.setValue("system.nofication",$values["system.nofication"].filter((_, i)=>i!=ind))}></button>
			</div>
		{/each}
	</div>
</main>
<style lang="scss">
	$light: (
        AccentFillColorDefaultBrush: var(--SystemAccentColorDark1),
		AccentFillColorSecondaryBrush: var(--SystemAccentColorDark2),
		AccentFillColorTertiaryBrush: var(--SystemAccentColorDark3),

		AccentFillColorBackgroundBrush: #ffffff,

		AccentHoverCoverColor: #ffffff15,
		AccentActiveCoverColor: #ffffff30,

		TextFillColorPrimaryBrush: #1a1a1a,
		TextFillColorSecondaryBrush: #5c5c5c,
		TextFillColorTertiaryBrush: #868686,
		TextFillColorDisabledBrush: #9b9b9b,

		TextOnAccentFillColorPrimaryBrush: #ffffff,
		TextOnAccentFillColorSecondaryBrush: #ffffff,
		TextOnAccentFillColorDisabledBrush: #ffffff,
		TextOnAccentFillColorSelectedTextBrush: #ffffff,

		SystemFillColorSuccessBrush: #0F7B0F,
		SystemFillColorCautionBrush: #9D5D00,
		SystemFillColorCriticalBrush: #C42B1C,

		SystemFillColorSuccessBackgroundBrush: #DFF6DD,
		SystemFillColorCautionBackgroundBrush: #FFF4CE,
		SystemFillColorCriticalBackgroundBrush: #FDE7E9,

		BackFillColor: #f3f3f3,
		ScrollbarColor: #8c8c8c,
		NavButtonHoverColor: #00000009,
		NavButtonActiveColor: #00000006,
    );
    $dark: (
        AccentFillColorDefaultBrush: var(--SystemAccentColorLight1),
		AccentFillColorSecondaryBrush: var(--SystemAccentColorLight2),
		AccentFillColorTertiaryBrush: var(--SystemAccentColorLight3),
		
		AccentFillColorBackgroundBrush: #2d2d2d,

		AccentHoverCoverColor: #00000010,
		AccentActiveCoverColor: #00000020,

		TextFillColorPrimaryBrush: #ffffff,
		TextFillColorSecondaryBrush: #cccccc,
		TextFillColorTertiaryBrush: #969696,
		TextFillColorDisabledBrush: #717171,

		TextOnAccentFillColorPrimaryBrush: #000000,
		TextOnAccentFillColorSecondaryBrush: #101010,
		TextOnAccentFillColorDisabledBrush: #969696,
		TextOnAccentFillColorSelectedTextBrush: #ffffff,

		SystemFillColorSuccessBrush: #6ccb5f,
		SystemFillColorCautionBrush: #fce100,
		SystemFillColorCriticalBrush: #ff99a4,

		SystemFillColorSuccessBackgroundBrush: #393d1b,
		SystemFillColorCautionBackgroundBrush: #433519,
		SystemFillColorCriticalBackgroundBrush: #442726,

		BackFillColor: #202020,
		ScrollbarColor: #9a9a9a,
		NavButtonHoverColor: #ffffff0e,
		NavButtonActiveColor: #ffffff0a,
    );
    @mixin apply-theme($m){@each $k, $v in $m {--#{$k}: #{$v};}}
    :global(.light){@include apply-theme($light);}
    :global(.dark){@include apply-theme($dark);}
    @media (prefers-color-scheme:light){:global(.system){@include apply-theme($light);}}
    @media (prefers-color-scheme:dark){:global(.system){@include apply-theme($dark);}}
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
			box-shadow: 0 0 4px 1px #00000030;
			&.l0{
				background-color: var(--AccentFillColorBackgroundBrush);
				.icon{
					color: var(--AccentFillColorBackgroundBrush);
					background-color: var(--AccentFillColorSecondaryBrush);
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
				padding: 0 0 1px 1px;
				margin: 9px 0 9px 9px;
				height: 16px;
				width: 16px;
				border-radius: 8px;
				color: var(--SystemFillColorCriticalBackgroundBrush);
				background-color: var(--SystemFillColorCriticalBrush);
			}
			.content{
				padding: 6px 0px;
				.description{
					font-size: 14px;
					font-variation-settings: 'wght' 400;
					word-wrap: break-word;
					overflow-wrap: anywhere;
				}
			}
			.close{
				flex: 0 0 34px;
				height: 34px;
				border-radius: 4px;
				align-self: flex-start;
				&:hover{
					background-color: var(--NavButtonHoverColor);
				}
			}
		}
	}
	.prevButton{
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
		background-color: var(--BackFillColor);
		color: var(--TextFillColorPrimaryBrush);
		width: 100vw;
		height: 100vh;
	}
	header{
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
				background-color: var(--NavButtonHoverColor);
				color: var(--TextFillColorSecondaryBrush);
			}
			&:active{
				background-color: var(--NavButtonActiveColor);
			}
			&:last-child:hover{
				background-color: var(--SystemFillColorCriticalBackgroundBrush);
				color: var(--SystemFillColorCriticalBrush);
			}
		}
	}
	nav{
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
				transition: all 0.1s ease-out, right 0s, top 0s;
				color: var(--TextOnAccentFillColorPrimaryBrush);
				&.l0{
					background-color: var(--AccentFillColorSecondaryBrush);
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
			}
			@container (max-width: 50px) {
				.badge{
					top: 4px;
					right: 4px;
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
				background-color: var(--NavButtonActiveColor);
			}
			&.Select,&.Select:active,&:not(.Select):hover{
				background-color: var(--NavButtonHoverColor);
			}
			&:not(.Select):active{
				background-color: var(--NavButtonActiveColor);
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