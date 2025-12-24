import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			pages: '../pywebwinui3/web',
			assets: '../pywebwinui3/web',
			fallback: undefined,
			precompress: false,
			strict: true
		})
	}
};

export default config;