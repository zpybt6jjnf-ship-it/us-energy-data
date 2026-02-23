<script lang="ts">
	import '../app.css';
	import Nav from '$components/layout/Nav.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div class="min-h-screen bg-surface">
	<Nav />
	<div class="pt-12 md:pl-48">
		<main class="max-w-[1400px] px-4 md:px-6 lg:px-8 py-4">
			{@render children()}
		</main>
		<footer class="md:hidden border-t border-border px-4 py-3 text-xs text-text-muted">
			Data: EIA · GitHub · Updated weekly
		</footer>
	</div>
</div>
