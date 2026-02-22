<script lang="ts">
	import { page } from '$app/stores';
	import { slide } from 'svelte/transition';

	const sections = [
		{ href: '/prices', label: 'Prices', color: '#2166ac', tooltip: 'Electricity costs by sector & state' },
		{ href: '/demand', label: 'Demand', color: '#1b9e77', tooltip: 'Consumption patterns & growth' },
		{ href: '/generation', label: 'Generation', color: '#e7a02f', tooltip: 'Power sources & capacity' },
		{ href: '/fuels', label: 'Fuels', color: '#a6611a', tooltip: 'Coal, gas & oil production' },
		{ href: '/reliability', label: 'Reliability', color: '#984ea3', tooltip: 'Outages & grid performance' },
	];

	let menuOpen = $state(false);

	let activeSection = $derived(
		sections.find((s) => $page.url.pathname.startsWith(s.href))
	);
</script>

<nav
	class="sticky top-0 z-40 bg-primary/95 backdrop-blur-md border-b border-white/5 shadow-[0_1px_12px_rgba(232,108,58,0.08)]"
>
	<div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-2">
		<a href="/" class="flex items-center gap-2 font-display text-base text-white no-underline hover:text-white/90">
			<!-- Energy bolt icon -->
			<svg class="h-5 w-5 text-accent" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
				<polygon points="11,1 5,11 9,11 7,19 15,9 11,9 13,1" />
			</svg>
			US Energy Data
		</a>

		<!-- Desktop nav -->
		<div class="hidden gap-1 md:flex">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					title={section.tooltip}
					class="relative rounded-full px-2.5 py-1 text-sm font-medium no-underline transition-colors
						{isActive
							? 'bg-accent/15 text-white'
							: 'text-white/70 hover:text-white hover:bg-white/5'}"
				>
					{section.label}
					{#if isActive}
						<span
							class="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-4 rounded-full bg-accent"
						></span>
					{/if}
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
		<div class="border-t border-white/10 px-4 py-2 md:hidden" transition:slide={{ duration: 200 }}>
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium no-underline
						{isActive
							? 'bg-accent/15 text-white'
							: 'text-white/70 hover:bg-white/5 hover:text-white'}"
					onclick={() => (menuOpen = false)}
				>
					{#if isActive}
						<span class="h-1.5 w-1.5 rounded-full" style="background-color: {section.color}"></span>
					{/if}
					{section.label}
				</a>
			{/each}
		</div>
	{/if}

	<!-- Section color indicator bar -->
	{#if activeSection}
		<div
			class="h-[3px] w-full"
			style="background-color: {activeSection.color}"
		></div>
	{/if}
</nav>
