<script lang="ts">
	import { page } from '$app/stores';

	const sections = [
		{ href: '/prices', label: 'Prices' },
		{ href: '/demand', label: 'Demand' },
		{ href: '/generation', label: 'Generation' },
		{ href: '/fuels', label: 'Fuels' },
		{ href: '/reliability', label: 'Reliability' },
	];

	let menuOpen = $state(false);
</script>

<nav class="sticky top-0 z-40 bg-primary shadow-[0_1px_3px_rgba(0,0,0,0.2)]">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<a href="/" class="font-display text-xl text-white no-underline hover:text-white/90">
			US Energy Data
		</a>

		<!-- Desktop nav -->
		<div class="hidden gap-1 md:flex">
			{#each sections as section}
				<a
					href={section.href}
					class="rounded-full px-3 py-1.5 text-sm font-medium no-underline transition-colors
						{$page.url.pathname.startsWith(section.href)
							? 'bg-white/10 text-white'
							: 'text-white/70 hover:text-white hover:bg-white/5'}"
				>
					{section.label}
				</a>
			{/each}
		</div>

		<!-- Mobile menu button -->
		<button
			class="rounded-md p-2 text-white/70 hover:bg-white/10 hover:text-white md:hidden"
			onclick={() => (menuOpen = !menuOpen)}
			aria-label="Toggle menu"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				{#if menuOpen}
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				{:else}
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
				{/if}
			</svg>
		</button>
	</div>

	<!-- Mobile menu -->
	{#if menuOpen}
		<div class="border-t border-white/10 px-4 py-2 md:hidden">
			{#each sections as section}
				<a
					href={section.href}
					class="block rounded-md px-3 py-2 text-sm font-medium no-underline
						{$page.url.pathname.startsWith(section.href)
							? 'bg-white/10 text-white'
							: 'text-white/70 hover:bg-white/5 hover:text-white'}"
					onclick={() => (menuOpen = false)}
				>
					{section.label}
				</a>
			{/each}
		</div>
	{/if}
</nav>
