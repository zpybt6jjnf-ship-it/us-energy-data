<script lang="ts">
	import '../app.css';
	import Nav from '$components/layout/Nav.svelte';
	import Footer from '$components/layout/Footer.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="min-h-screen bg-surface">
	<Nav />
	<div class="pt-14">
		<main class="px-4 md:px-6 lg:px-8 py-8">
			{@render children()}
		</main>
		<Footer />
	</div>
</div>
