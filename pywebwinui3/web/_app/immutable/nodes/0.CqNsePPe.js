import{c as g,a as d,f as m}from"../chunks/fGsU50sd.js";import{D as b,E as h,a as v,H as y,h as u,F as _,G as k,I as c,J as f,K as p,e as w,w as x,L as E,x as F,z as C,M as S}from"../chunks/B8k5Ccj7.js";import{B as T}from"../chunks/CEpW9fsN.js";import{o as B}from"../chunks/DbLPBgK4.js";function M(n,o,...r){var a=new T(n);b(()=>{const t=o()??null;a.ensure(t,t&&(e=>t(e,...r)))},h)}function z(n,o){let r=null,a=u;var t;if(u){r=w;for(var e=_(document.head);e!==null&&(e.nodeType!==k||e.data!==n);)e=c(e);if(e===null)f(!1);else{var s=c(e);e.remove(),p(s)}}u||(t=document.head.appendChild(v()));try{b(()=>o(t),y)}finally{a&&(f(!0),p(r))}}const A=!0,N=Object.freeze(Object.defineProperty({__proto__:null,prerender:A},Symbol.toStringTag,{value:"Module"}));var D=m(`<link rel="icon" href="data:,"/> <style>@import url(./Pretendard/Variable-dynamic-subset.min.css);
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
		}</style>`,1);function H(n,o){x(o,!0),E(()=>{const t=e=>{const s=e.target;if(!(s instanceof Element))return;const l=s.closest("a[href]");if(!(l instanceof HTMLAnchorElement))return;const i=l.getAttribute("href")||"";!i||i.startsWith("#")||/^(about|data|file|qrc):/i.test(i)||/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(i)&&(e.preventDefault(),e.stopPropagation(),B(i,l.getAttribute("target")||"_blank"))};return document.addEventListener("click",t,!0),()=>document.removeEventListener("click",t,!0)});var r=g();z("12qhfyh",t=>{var e=D();S(2),d(t,e)});var a=F(r);M(a,()=>o.children),d(n,r),C()}export{H as component,N as universal};
