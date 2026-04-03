<script context="module" lang="ts">
	import { writable, get } from 'svelte/store';
	import '../lib/ThemeResources.scss';

	export const values = writable<Record<string, any>>({
		"system_goBack": true,
		"system_pinTop": true,
		"system_title": null,
		"system_icon": null,
		"system_theme": "system",
		"system_theme_resolved": "dark",
		"system_accent": ["#fff","#fff","#fff","#888","#000","#000","#000"],
		"system_pin": false,
		"system_pages": null,
		"system_settings": null,
		"system_nofication": [],
		"system_window_width": 900,
		"system_window_height": 600
	});

	const hasValue = (dict: Record<string, any>, key: string) =>
		Object.prototype.hasOwnProperty.call(dict, key);
	type ValuePathToken = string | number;

	const parseValuePath = (path: string): ValuePathToken[] | null => {
		if (typeof path !== 'string' || !path.includes('[')) {
			return null;
		}

		const firstBracket = path.indexOf('[');
		const rootKey = path.slice(0, firstBracket);
		if (!rootKey) {
			return null;
		}

		const tokens: ValuePathToken[] = [rootKey];
		let cursor = firstBracket;
		while (cursor < path.length) {
			if (path[cursor] !== '[') {
				return null;
			}

			const end = path.indexOf(']', cursor + 1);
			if (end === -1) {
				return null;
			}

			const raw = path.slice(cursor + 1, end).trim();
			if (!raw) {
				return null;
			}

			if (/^\d+$/.test(raw)) {
				tokens.push(Number(raw));
			} else if (
				(raw.startsWith('"') && raw.endsWith('"'))
				|| (raw.startsWith("'") && raw.endsWith("'"))
			) {
				tokens.push(raw.slice(1, -1));
			} else {
				tokens.push(raw);
			}

			cursor = end + 1;
		}

		return tokens;
	};

	const clonePathContainer = (value: any, nextToken?: ValuePathToken) => {
		if (Array.isArray(value)) {
			return [...value];
		}
		if (value && typeof value === 'object') {
			return { ...value };
		}
		return typeof nextToken === 'number' ? [] : {};
	};

	export const getValueByPath = (source: Record<string, any>, path: any) => {
		if (typeof path !== 'string') {
			return path;
		}

		const tokens = parseValuePath(path);
		if (!tokens) {
			return source[path];
		}

		let current: any = source;
		for (const token of tokens) {
			if (current == null) {
				return undefined;
			}
			current = current[token as keyof typeof current];
		}
		return current;
	};

	export const setValueByPath = (source: Record<string, any>, path: string, value: any) => {
		const tokens = parseValuePath(path);
		if (!tokens) {
			source[path] = value;
			return;
		}

		const [rootKey, ...segments] = tokens;
		if (!segments.length) {
			source[rootKey as string] = value;
			return;
		}

		const rootSource = source[rootKey as string];
		const rootClone: any = clonePathContainer(rootSource, segments[0]);
		let sourceCursor: any = rootSource;
		let cursor: any = rootClone;

		for (let index = 0; index < segments.length - 1; index += 1) {
			const token = segments[index];
			const nextToken = segments[index + 1];
			const sourceValue = sourceCursor == null ? undefined : sourceCursor[token as keyof typeof sourceCursor];
			const clonedValue = clonePathContainer(sourceValue, nextToken);

			if (Array.isArray(cursor) && typeof token === 'number') {
				while (cursor.length <= token) {
					cursor.push(undefined);
				}
				cursor[token] = clonedValue;
			} else {
				cursor[token as keyof typeof cursor] = clonedValue;
			}

			cursor = clonedValue;
			sourceCursor = sourceValue;
		}

		const lastToken = segments[segments.length - 1];
		if (Array.isArray(cursor) && typeof lastToken === 'number') {
			while (cursor.length <= lastToken) {
				cursor.push(undefined);
			}
			cursor[lastToken] = value;
		} else {
			cursor[lastToken as keyof typeof cursor] = value;
		}

		source[rootKey as string] = rootClone;
	};

	const expressionCache = new Map<string, (valueMap: Record<string, any>) => any>();
	const formatPlanCache = new Map<string, any>();
	const formatCache = new Map<string, { signature: string; value: any }>();
	const attributeCache = new WeakMap<object, { signature: string; value: Record<string, any> }>();
	const componentCache = new WeakMap<object, { signature: string; value: Record<string, any> }>();
	const exactTemplatePattern = /^(?<!\\)\{([^}]+)\}$/;
	const inlineTemplatePattern = /(?<!\\){(.*?)}/g;
	const escapedTemplatePattern = /\\({.*?})/g;
	const directKeyPattern = /^[A-Za-z_$][\w$]*$/;
	const DEFAULT_ACCENT_PALETTE = ["#fff", "#fff", "#fff", "#888", "#000", "#000", "#000"];
	const ACCENT_VARIANTS = ['Light3', 'Light2', 'Light1', '', 'Dark1', 'Dark2', 'Dark3'];

	let currentValues = get(values);
	let trackedValues: Record<string, any> = { ...currentValues };
	let globalValueVersion = 0;
	const valueVersions = new Map<string, number>();

	values.subscribe((nextValues) => {
		currentValues = nextValues;
		const nextTrackedValues = { ...nextValues };
		const keys = new Set([
			...Object.keys(trackedValues),
			...Object.keys(nextTrackedValues)
		]);

		let changed = false;
		for (const key of keys) {
			if (trackedValues[key] === nextTrackedValues[key]) {
				continue;
			}
			valueVersions.set(key, (valueVersions.get(key) ?? 0) + 1);
			changed = true;
		}

		if (changed) {
			globalValueVersion += 1;
		}

		trackedValues = nextTrackedValues;
	});

	const evaluateExpression = (expression: string, valueMap: Record<string, any>) => {
		let evaluator = expressionCache.get(expression);
		if (!evaluator) {
			evaluator = Function('v', `with(v){ return ${expression} }`) as (valueMap: Record<string, any>) => any;
			expressionCache.set(expression, evaluator);
		}
		return evaluator(valueMap);
	};

	const unescapeTemplateText = (text: string) => text.replace(escapedTemplatePattern, "$1");

	const compileFormatPlan = (text: string) => {
		if (!text.includes('{')) {
			return { kind: 'raw' } as const;
		}

		const exactTemplateMatch = text.match(exactTemplatePattern);
		if (exactTemplateMatch) {
			const token = exactTemplateMatch[1];
			if (directKeyPattern.test(token)) {
				return { kind: 'exact-key', key: token } as const;
			}
			return { kind: 'exact-expression', expression: token } as const;
		}

		const parts: Array<string | { raw: string; key?: string; expression?: string }> = [];
		const dependencies = new Set<string>();
		let hasExpression = false;
		let lastIndex = 0;

		for (const match of text.matchAll(inlineTemplatePattern)) {
			const fullMatch = match[0];
			const token = match[1];
			const index = match.index ?? 0;

			if (index > lastIndex) {
				parts.push(unescapeTemplateText(text.slice(lastIndex, index)));
			}

			if (directKeyPattern.test(token)) {
				parts.push({ raw: fullMatch, key: token });
				dependencies.add(token);
			} else {
				parts.push({ raw: fullMatch, expression: token });
				hasExpression = true;
			}

			lastIndex = index + fullMatch.length;
		}

		if (lastIndex < text.length) {
			parts.push(unescapeTemplateText(text.slice(lastIndex)));
		}

		return {
			kind: 'template',
			parts,
			dependencies: hasExpression ? null : [...dependencies]
		} as const;
	};

	const getFormatPlan = (text: string) => {
		let plan = formatPlanCache.get(text);
		if (!plan) {
			plan = compileFormatPlan(text);
			formatPlanCache.set(text, plan);
		}
		return plan;
	};

	const getFormatSignature = (text: any) => {
		if (typeof text !== 'string') {
			return '';
		}

		const plan = getFormatPlan(text);
		if (plan.kind === 'raw') {
			return '';
		}

		if (plan.kind === 'exact-expression') {
			return `g:${globalValueVersion}`;
		}

		if (plan.kind === 'exact-key') {
			return `${plan.key}:${valueVersions.get(plan.key) ?? 0}`;
		}

		if (plan.dependencies == null) {
			return `g:${globalValueVersion}`;
		}

		return plan.dependencies
			.map((key: string) => `${key}:${valueVersions.get(key) ?? 0}`)
			.join('|');
	};

	export const format = (text: any) => {
		if (typeof text !== 'string') {
			return text;
		}

		const plan = getFormatPlan(text);
		if (plan.kind === 'raw') {
			return text;
		}

		const signature = getFormatSignature(text);
		const cached = formatCache.get(text);
		if (cached && cached.signature === signature) {
			return cached.value;
		}

		let result = text;

		if (plan.kind === 'exact-key') {
			result = hasValue(currentValues, plan.key) ? currentValues[plan.key] : text;
		} else if (plan.kind === 'exact-expression') {
			try {
				result = evaluateExpression(plan.expression, currentValues);
			} catch (e) {
				result = text;
			}
		} else {
			result = plan.parts.map((part: any) => {
				if (typeof part === 'string') {
					return part;
				}
				if (part.key) {
					return hasValue(currentValues, part.key) ? currentValues[part.key] : part.raw;
				}
				try {
					return evaluateExpression(part.expression, currentValues);
				} catch (e) {
					return part.raw;
				}
			}).join('');
		}

		formatCache.set(text, { signature, value: result });
		return result;
	};

	export const formatAttributes = (attrs: Record<string, any> = {}) => {
		const signature = Object.entries(attrs)
			.map(([key, value]) => `${key}:${getFormatSignature(value)}`)
			.join('|');

		const cached = attributeCache.get(attrs);
		if (cached && cached.signature === signature) {
			return cached.value;
		}

		let formattedAttrs = attrs;
		for (const [key, value] of Object.entries(attrs)) {
			const formattedValue = format(value);
			if (formattedValue === value) {
				continue;
			}

			if (formattedAttrs === attrs) {
				formattedAttrs = { ...attrs };
			}
			formattedAttrs[key] = formattedValue;
		}

		attributeCache.set(attrs, {
			signature,
			value: formattedAttrs
		});
		return formattedAttrs;
	};

	export const formatComponentSource = (source: Record<string, any>) => {
		const signature = `${Object.entries(source.attr ?? {})
			.map(([key, value]) => `${key}:${getFormatSignature(value)}`)
			.join('|')}::${getFormatSignature(source.text)}`;

		const cached = componentCache.get(source);
		if (cached && cached.signature === signature) {
			return cached.value;
		}

		const formattedAttr = formatAttributes(source.attr ?? {});
		const formattedText = format(source.text);
		const formattedSource = formattedAttr === source.attr && formattedText === source.text
			? source
			: {
				tag: source.tag,
				attr: formattedAttr,
				text: formattedText,
				child: source.child
			};

		componentCache.set(source, {
			signature,
			value: formattedSource
		});
		return formattedSource;
	};
</script>
<script lang="ts">
	import { onMount } from 'svelte';
	import { get as getStoreValue } from 'svelte/store';

	import Component from "../lib/Component.svelte";
	import { getDesktopApi, getDesktopResourceContextVersion, installDesktopWindowBindings, onDesktopResourceContextChange, queueDesktopSync, resolveDesktopResource } from '../lib/desktop';

	const desktopApi = getDesktopApi();
	const WINDOW_SIZE_KEYS = new Set(['system_window_width', 'system_window_height']);

	const NOTICE_ICONS = ["", "", "", ""];

	let isNavOpen = true;

	let resolvedSystemIcon = '';
	let systemIconResolveRequest = 0;
	let systemIconSource: unknown;
	let systemIconResourceContextVersion = getDesktopResourceContextVersion();
	let systemIconResolvedContextVersion = -1;
	let sortedPageKeys: string[] = [];
	let accentStyle = '';
	let currentThemeClass = 'dark';
	let settingsPage: Record<string, any> | null = null;

	$: {
		const source = $values["system_icon"];
		if (source !== systemIconSource || systemIconResolvedContextVersion !== systemIconResourceContextVersion) {
			systemIconSource = source;
			systemIconResolvedContextVersion = systemIconResourceContextVersion;
			const requestId = ++systemIconResolveRequest;

			if (typeof source !== 'string' || !source) {
				resolvedSystemIcon = source == null ? '' : String(source);
			} else {
				void resolveDesktopResource(source).then((nextSource) => {
					if (requestId === systemIconResolveRequest) {
						resolvedSystemIcon = nextSource || source;
					}
				});
			}
		}
	}

	$: {
		const pages = $values["system_pages"] ?? {};
		sortedPageKeys = Object.keys(pages).sort();
	}

	$: {
		const accentPalette = Array.isArray($values["system_accent"]) ? $values["system_accent"] : DEFAULT_ACCENT_PALETTE;
		accentStyle = `${ACCENT_VARIANTS
			.map((variant, index) => `--SystemAccentColor${variant}:${accentPalette[index]};`)
			.join('')}`
			+ `--AccentFillColorLightSecondaryBrush: ${accentPalette[1]}E6;`
			+ `--AccentFillColorLightTertiaryBrush: ${accentPalette[1]}CC;`
			+ `--AccentFillColorDarkSecondaryBrush: ${accentPalette[4]}E6;`
			+ `--AccentFillColorDarkTertiaryBrush: ${accentPalette[4]}CC;`;
	}

	$: currentThemeClass = $values["system_theme"] === "system"
		? ($values["system_theme_resolved"] ?? "dark")
		: ($values["system_theme"] ?? "dark");

	$: settingsPage = $values["system_settings"] ?? null;

	const applyPatch = (patch: Record<string, any>) => {
		if (!patch || Object.keys(patch).length === 0) {
			return;
		}
		values.update(dict=>{
			for (const [key, value] of Object.entries(patch)) {
				setValueByPath(dict, key, value);
			}
			return dict;
		});
	};

	let pendingWindowSizePatch: Record<string, any> | null = null;
	let pendingWindowSizeFrame = 0;

	const flushPendingWindowSizePatch = () => {
		if (!pendingWindowSizePatch) {
			pendingWindowSizeFrame = 0;
			return;
		}

		const patch = pendingWindowSizePatch;
		pendingWindowSizePatch = null;
		pendingWindowSizeFrame = 0;
		applyPatch(patch);
	};

	const queueWindowSizePatch = (patch: Record<string, any>) => {
		pendingWindowSizePatch = {
			...(pendingWindowSizePatch ?? {}),
			...patch
		};

		if (pendingWindowSizeFrame) {
			return;
		}

		pendingWindowSizeFrame = window.requestAnimationFrame(() => {
			flushPendingWindowSizePatch();
		});
	};

	const withDesktopApi = (callback: (api: Awaited<typeof desktopApi>) => void) => {
		void desktopApi.then(callback);
	};

	onMount(() => {
		const cleanupWindowBindings = installDesktopWindowBindings();
		const cleanupResourceContext = onDesktopResourceContextChange((version) => {
			systemIconResourceContextVersion = version;
		});

		const init = async () => {
			window.applyBackendPatch = (patch: Record<string, any>) => {
				const nextPatch = patch ?? {};
				const keys = Object.keys(nextPatch);
				if (keys.length === 0) {
					return;
				}

				if (keys.every((key) => WINDOW_SIZE_KEYS.has(key))) {
					queueWindowSizePatch(nextPatch);
					return;
				}

				if (pendingWindowSizeFrame) {
					window.cancelAnimationFrame(pendingWindowSizeFrame);
					flushPendingWindowSizePatch();
				}

				applyPatch(nextPatch);
			};

			window.syncValue = (target:string, value:any, sync=true) => {
				const nextValue = value;
				if(!target) return;
				if(target.endsWith("_Temp") && getValueByPath(getStoreValue(values), target) === nextValue) return;
				values.update(dict=>{
					setValueByPath(dict, target, nextValue);
					return dict;
				});
				if(target.endsWith("_Temp")) return;
				if(sync) queueDesktopSync(target, nextValue);
			};
			history.replaceState({i:0},"");
			hashChange();
			let api = await desktopApi;
			let appConfig = await api.init();
			applyPatch(appConfig);
			api.frontendReady();
		};

		void init();

		return () => {
			if (pendingWindowSizeFrame) {
				window.cancelAnimationFrame(pendingWindowSizeFrame);
			}
			cleanupWindowBindings();
			cleanupResourceContext();
		};
	});

	let hash:string;
	let RecentPages = 0;
	const hashChange = () => {
		if(location.hash==`#${hash}`) return;
		hash = location.hash.replace("#","");
		if(history.state==null) history.replaceState({i:RecentPages+1}, "");
		RecentPages = history.state?.i ?? 0;
	};
</script>
<svelte:window on:hashchange={hashChange}></svelte:window>
<main class={currentThemeClass} style="
	grid-template-columns: {isNavOpen ? 230 : 50}px 1fr;
	{accentStyle}
">
	<header>
		<div class="pywebview-drag-region"></div>
		{#if $values["system_goBack"]}
			<button class="prevButton" on:click={()=>history.back()} disabled={!RecentPages}>
				<span class="icon"></span>
			</button>
		{/if}
		<div class="title pywebview-drag-region">
			<img src={resolvedSystemIcon} alt="" style="opacity: {resolvedSystemIcon?1:0};"/>
			<p>{$values["system_title"]??""}</p>
		</div>
		{#if $values["system_pinTop"]}
			<button on:click={()=>withDesktopApi(api => api.pin(!$values["system_pin"]))}>{$values["system_pin"]?'':''}</button>
		{/if}
		<button on:click={()=>withDesktopApi(api => api.minimize())}></button>
		<button on:click={()=>withDesktopApi(api => api.destroy())}></button>
	</header>
	<nav style="grid-template-rows: 40px 1fr {$values['system_settings'] ? '40px' : ''};">
		<button class="menuButton" style="width: 40px" on:click={()=>isNavOpen=!isNavOpen}>
			<span class="icon"></span>
		</button>
		<section>
			{#each sortedPageKeys as key}
				{@const val = $values["system_pages"][key]}
				{@const badgeState = format(val['attr']?.['state']??"")}
				{@const badgeText = format(val["attr"]?.["badge"]??"")??""}
				<button class:settingButton={val["attr"]?.["icon"]==""} class:Select={hash==key} on:click={()=>location.hash=key}>
					<span class="icon">{val["attr"]?.["icon"] ?? ""}</span>
					<span>{val["attr"]?.["name"] ?? key}</span>
				{#if badgeState !== "" && badgeState != null}
					<span class="badge l{badgeState}">{badgeText}</span>
				{/if}
				</button>
			{/each}
		</section>
		{#if settingsPage}
			{@const path = settingsPage["attr"]?.["path"] ?? "settings"}
			{@const icon = settingsPage["attr"]?.["icon"] ?? ""}
			{@const state = settingsPage["attr"]?.["state"]}
			{@const settingsBadgeState = format(state??"")}
			{@const settingsBadgeText = format(settingsPage["attr"]?.["badge"]??"")??""}
			<button class:settingButton={icon==""} class:Select={hash==path} on:click={()=>location.hash=path}>
				<span class="icon">{icon}</span>
				<span>{settingsPage["attr"]?.["name"] ?? "Settings"}</span>
				{#if settingsBadgeState !== "" && settingsBadgeState != null}
					<span class="badge l{settingsBadgeState}">{settingsBadgeText}</span>
				{/if}
			</button>
		{/if}
	</nav>
	{#key hash}
		{#if settingsPage?.["attr"]?.["path"]==hash}
			<Component rawData={settingsPage}/>
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
				<span class="icon">{NOTICE_ICONS[level]}</span>
				<span class="content">
					<span class="title">{title}</span>
					<span class="description">{description}</span>
				</span>
				{#if item}
					<span class="item">
						<Component rawData={item}/>
					</span>
				{/if}
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
				flex-wrap: wrap;
				align-items: baseline;
				.title{
					margin: 6px 8px 0 0;
					line-height: 20px;
				}
				.description{
					font-size: 14px;
					font-variation-settings: 'wght' 400;
					overflow-wrap: anywhere;
					margin: 4px 0 6px 0;
				}
			}
			.item{
				flex: 0 0 auto;
				margin: 2px 0 2px 0;
			}
			.close{
				width: 34px;
				height: 34px;
				flex: 0 0 34px;
				border-radius: 4px;
				&:hover{
					background-color: var(--SubtleFillColorSecondaryBrush);
				}
				&:active{
					background-color: var(--SubtleFillColorTertiaryBrush);
				}
			}
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
			z-index: 1;
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
				transition: all 0.2s ease, color 0.1s ease, right 0s, top 0s, width 0s, height 0s;
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
			&:active{
				color: currentColor;
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
		}
		&:active{
			color: currentColor;
				&>.icon{
				animation: none;
				scale: 80% 100%;
				translate: 12% 0%;
			}
		}
	}
	@keyframes settingRotate {
		0%{
			transform: rotate(0);
		}
		100%{
			transform: rotate(120deg);
		}
	}
	.settingButton{
		top: -0.6px;
		padding: 0 0 0.6px 0;
		&>.icon{
			left: 0;
			animation : settingRotate 0.6s forwards alternate;
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
</style>
