<script lang="ts">
	import { onMount } from 'svelte';
	import { openLink } from '$lib/desktop';

	let { children } = $props();

	onMount(() => {
		const handleClick = (event: MouseEvent) => {
			const target = event.target;
			if (!(target instanceof Element)) return;

			const anchor = target.closest('a[href]');
			if (!(anchor instanceof HTMLAnchorElement)) return;

			const href = anchor.getAttribute('href') || '';
			if (!href || href.startsWith('#')) return;
			if (/^(about|data|file|qrc):/i.test(href)) return;
			if (!/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(href)) return;

			event.preventDefault();
			event.stopPropagation();
			openLink(href, anchor.getAttribute('target') || '_blank');
		};

		document.addEventListener('click', handleClick, true);
		return () => document.removeEventListener('click', handleClick, true);
	});
</script>

<svelte:head>
	<link rel="icon" href="data:,">
	<style>
		@import url(./Pretendard/Variable-dynamic-subset.min.css);
		@font-face {
			font-family: 'Segoe Fluent Icons';
			src: url(./SegoeFluentIcons.ttf);
			ascent-override: 80%;
		}
		*,::before,::after{
			font-family: 'Segoe Fluent Icons', "Pretendard Variable";
			font-variation-settings: 'wght' 550;
			background-color: transparent;
			position: relative;
			margin: 0;
			padding: 0;
			word-wrap: break-word;
			overflow-wrap: break-word;
			box-sizing: border-box;
			line-height: 1.2;
			color: inherit;
			transition: all 0.2s ease, color 0.1s ease, width 0s, height 0s;
		}
		::-webkit-scrollbar{
			width: 4px;
		}
		::-webkit-scrollbar-thumb{
			background-clip: padding-box;
			border-radius: 7px;
			border: 1px solid transparent;
			background-color: var(--ControlStrongFillColorDefaultBrush);
		}
		:disabled,.disabled {
			cursor: not-allowed;
			pointer-events: none;
			opacity: 0.5;
		}
		button,label{
			cursor: pointer;
			user-select: none;
		}
		input,textarea,button{
			outline: none;
			border: none;
		}
		:focus-visible::after {
			z-index: 200;
			content: "";
			position: absolute;
			inset: 0px;
			border: 2px solid var(--FocusStrokeColorOuterBrush);
			border-radius: 4px;
			pointer-events: none;
		}
		body{
			background-color: var(--SolidBackgroundFillColorBaseBrush);
		}
	</style>
</svelte:head>

{@render children()}
