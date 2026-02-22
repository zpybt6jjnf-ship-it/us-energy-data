<script lang="ts">
	import '../app.css';
	import Nav from '$components/layout/Nav.svelte';
	import Footer from '$components/layout/Footer.svelte';
	import { page } from '$app/stores';
	import { fade } from 'svelte/transition';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="flex min-h-screen flex-col bg-surface">
	<Nav />
	<main class="mx-auto w-full max-w-5xl flex-1 px-4 py-4">
		{#key $page.url.pathname}
			<div in:fade={{ duration: 200, delay: 100 }} out:fade={{ duration: 100 }}>
				{@render children()}
			</div>
		{/key}
	</main>
	<Footer />
</div>
