<script lang="ts">
	import '../app.css';
	import Nav from '$components/layout/Nav.svelte';
	import Footer from '$components/layout/Footer.svelte';
	import { page } from '$app/stores';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	const isEmbed = $derived($page.url.searchParams.get('embed') === 'true');

	$effect(() => {
		if (isEmbed) {
			const hash = $page.url.hash;
			if (hash) {
				// Wait for content to render before scrolling
				requestAnimationFrame(() => {
					document.querySelector(hash)?.scrollIntoView({ behavior: 'smooth' });
				});
			}
		}
	});
</script>

{#if isEmbed}
	<div class="bg-surface p-4" data-embed>
		{@render children()}
	</div>
{:else}
	<div class="min-h-screen bg-surface">
		<Nav />
		<div class="pt-14">
			<main class="px-4 md:px-6 lg:px-8 py-8">
				{@render children()}
			</main>
			<Footer />
		</div>
	</div>
{/if}

<style>
	:global([data-embed] .prose-width) {
		display: none;
	}
	:global([data-embed] .section-heading) {
		display: none;
	}
</style>
