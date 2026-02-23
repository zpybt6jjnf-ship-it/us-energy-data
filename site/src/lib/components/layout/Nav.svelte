<script lang="ts">
	import { page } from '$app/stores';

	const sections = [
		{ href: '/prices', label: 'Prices & Bills', color: '#5B8DEF' },
		{ href: '/demand', label: 'Demand', color: '#00E68A' },
		{ href: '/generation', label: 'Generation', color: '#FBBF24' },
		{ href: '/fuels', label: 'Fuels', color: '#FB923C' },
		{ href: '/reliability', label: 'Reliability', color: '#C084FC' },
	];

	let drawerOpen = $state(false);

	function closeDrawer() {
		drawerOpen = false;
	}
</script>

<!-- Top nav bar -->
<header class="fixed top-0 left-0 right-0 z-40 bg-surface-card/80 backdrop-blur-xl border-b border-transparent">
	<div class="flex items-center h-12 px-4 md:px-6 max-w-[1400px] mx-auto">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2 text-sm font-bold font-display text-text no-underline hover:text-accent shrink-0" onclick={closeDrawer}>
			<svg class="h-5 w-5 shrink-0" viewBox="0 0 44 44" aria-hidden="true">
				<rect width="44" height="44" fill="#1a1a2e" />
				<defs>
					<linearGradient id="nav-logo-grad" x1="0%" y1="0%" x2="100%" y2="0%">
						<stop offset="0%" stop-color="#2a9d8f" />
						<stop offset="50%" stop-color="#e9c46a" />
						<stop offset="100%" stop-color="#e76f51" />
					</linearGradient>
				</defs>
				<path d="M 0,30.8 L 3.52,28.6 L 7.92,33 L 12.32,22 L 16.72,26.4 L 22,13.2 L 27.28,24.2 L 31.68,19.8 L 36.08,26.4 L 40.48,24.2 L 44,28.6" stroke="url(#nav-logo-grad)" stroke-width="1.32" fill="none" stroke-linejoin="round" />
			</svg>
			Bottlenecks Labs
		</a>

		<!-- Desktop nav links -->
		<nav class="hidden md:flex items-center gap-1 ml-6">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="relative rounded-full px-3 py-1 text-sm no-underline transition-all
						{isActive
							? 'bg-accent/15 text-accent font-medium'
							: 'text-text-secondary hover:text-text hover:bg-surface-alt/50'}"
				>
					{#if isActive}
						<span class="absolute inset-0 rounded-full bg-accent/10 blur-sm"></span>
					{/if}
					<span class="relative">{section.label}</span>
				</a>
			{/each}
		</nav>

		<!-- Spacer -->
		<div class="flex-1"></div>

		<!-- Attribution links (desktop) -->
		<div class="hidden md:flex items-center gap-1.5 text-[11px] text-text-muted">
			<a href="https://www.eia.gov/" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-accent">Data: EIA</a>
			<span class="text-text-muted/40">·</span>
			<a href="https://github.com/us-energy-data" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-accent">GitHub</a>
		</div>

		<!-- Mobile hamburger -->
		<button
			class="ml-3 rounded-md p-2 text-text-secondary hover:bg-surface-alt hover:text-text md:hidden"
			onclick={() => (drawerOpen = !drawerOpen)}
			aria-label="Toggle menu"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				{#if drawerOpen}
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				{:else}
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
				{/if}
			</svg>
		</button>
	</div>

	<!-- Gradient bottom border -->
	<div class="h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent"></div>
</header>

<!-- Mobile drawer overlay -->
{#if drawerOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm md:hidden"
		onclick={closeDrawer}
		onkeydown={(e) => e.key === 'Escape' && closeDrawer()}
	></div>

	<nav class="fixed left-0 top-12 bottom-0 z-40 w-64 bg-surface-card border-r border-border md:hidden flex flex-col">
		<div class="flex-1 py-3 px-2 space-y-0.5">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm no-underline
						{isActive
							? 'bg-accent/15 text-accent font-medium'
							: 'text-text-secondary hover:bg-surface-alt/50 hover:text-text'}"
					onclick={closeDrawer}
				>
					<span class="h-1.5 w-1.5 rounded-full shrink-0" style="background-color: {section.color}"></span>
					{section.label}
				</a>
			{/each}
		</div>

		<!-- Bottom attribution -->
		<div class="border-t border-border px-3 py-3 space-y-1">
			<div class="flex items-center gap-1.5 text-[11px] text-text-muted">
				<a href="https://www.eia.gov/" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-accent">Data: EIA</a>
				<span class="text-text-muted/40">·</span>
				<a href="https://github.com/us-energy-data" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-accent">GitHub</a>
			</div>
			<p class="text-[11px] text-text-muted/60">Updated weekly</p>
		</div>
	</nav>
{/if}
