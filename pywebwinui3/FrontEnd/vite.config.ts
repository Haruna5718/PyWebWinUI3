import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
	base: "./",
	plugins: [
		svelte({
			onwarn: (warning, handler) => {
				if (warning.code.startsWith('a11y-')) return
				handler(warning)
			}
		}),
		// {
		// 	name: 'single-file-build',
		// 	enforce: 'post',
		// 	apply: 'build',
		// 	generateBundle(_, bundle) {
		// 		let htmlFile: string | undefined
		// 		let jsCode = ''
		// 		let cssCode = ''

		// 		for (const [fileName, asset] of Object.entries(bundle)) {
		// 			if (fileName.endsWith('.js') && typeof asset === 'object' && asset !== null && 'code' in asset) {
		// 				jsCode += (asset as { code: string }).code
		// 				delete bundle[fileName]
		// 			}
		// 			if (fileName.endsWith('.css') && typeof asset === 'object' && asset !== null && 'source' in asset) {
		// 				cssCode += (asset as { source: string }).source
		// 				delete bundle[fileName]
		// 			}
		// 			if (fileName.endsWith('.html') && typeof asset === 'object' && asset !== null && 'source' in asset) {
		// 				htmlFile = fileName
		// 			}
		// 		}

		// 		if (htmlFile) {
		// 			const htmlAsset = bundle[htmlFile]
		// 			if (typeof htmlAsset === 'object' && htmlAsset !== null && 'source' in htmlAsset) {
		// 				let html = String((htmlAsset as { source: string }).source)
		// 				html = html
		// 					.replace(/<link rel="stylesheet".*?>/g, () => `<style>${cssCode}</style>`)
		// 					.replace(/<script type="module".*?src=".*?"><\/script>/g, () => `<script type="module">${jsCode}</script>`)
		// 				;(htmlAsset as { source: string }).source = html
		// 			}
		// 		}
		// 	},
		// }
	],
	build: {
		outDir: '../web',
		emptyOutDir: true,
		rollupOptions: {
			output: {
				entryFileNames: 'PYWEBWINUI3/bundle.js',
				chunkFileNames: 'PYWEBWINUI3/bundle.js',
				// assetFileNames: 'bundle.[ext]',
				assetFileNames: (assetInfo) => (assetInfo.name&&assetInfo.name.endsWith('.css'))?'PYWEBWINUI3/bundle.css':'PYWEBWINUI3/[name].[ext]'
			},
		},
	},
})
