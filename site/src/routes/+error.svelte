<script lang="ts">
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>Error {$page.status} — US Energy Data</title>
</svelte:head>

<div class="prose-width py-16 text-center">
	<h1 class="text-4xl font-display tracking-tight text-text">{$page.status}</h1>
	<p class="narrative-text mt-4">{$page.error?.message ?? 'Something went wrong.'}</p>
	<a href="/" class="mt-6 inline-block text-accent hover:text-accent-light no-underline font-medium">&larr; Back to homepage</a>
</div>
