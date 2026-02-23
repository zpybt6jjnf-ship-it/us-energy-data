<script lang="ts">
	import { page } from '$app/stores';
	import Logo from './Logo.svelte';

	const sections = [
		{ href: '/prices', label: 'Prices & Bills' },
		{ href: '/demand', label: 'Demand' },
		{ href: '/generation', label: 'Generation' },
		{ href: '/fuels', label: 'Fuels' },
		{ href: '/reliability', label: 'Reliability' },
	];

	let drawerOpen = $state(false);

	function closeDrawer() {
		drawerOpen = false;
	}
</script>

<!-- Top nav bar -->
<header class="fixed top-0 left-0 right-0 z-40 bg-surface/95 backdrop-blur-sm border-b border-border">
	<div class="flex items-center h-14 px-4 md:px-6 max-w-[1100px] mx-auto">
		<!-- Logo -->
		<a href="/" class="flex items-center gap-2 text-sm text-text no-underline hover:text-text-secondary shrink-0" style="font-family: 'Space Mono', monospace; font-weight: 700; letter-spacing: 0.02em;" onclick={closeDrawer}>
			<Logo id="nav-logo-grad" />
			Bottlenecks Lab
		</a>

		<!-- Desktop nav links -->
		<nav class="hidden md:flex items-center gap-1 ml-6 self-stretch">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="relative flex items-center h-full px-3 text-sm no-underline transition-colors duration-200
						{isActive
							? 'text-text font-semibold'
							: 'text-text-muted hover:text-text'}"
				>
					{section.label}
					{#if isActive}
						<span class="absolute bottom-[-1px] left-3 right-3 h-0.5 bg-accent rounded-full"></span>
					{/if}
				</a>
			{/each}
		</nav>

		<!-- Spacer -->
		<div class="flex-1"></div>

		<!-- Attribution links (desktop) -->
		<div class="hidden md:flex items-center gap-1.5 text-[11px] text-text-muted">
			<a href="https://www.eia.gov/" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">Data: EIA</a>
			<span class="text-text-muted/40">·</span>
			<a href="https://github.com/us-energy-data" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">GitHub</a>
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
</header>

<!-- Mobile drawer overlay -->
{#if drawerOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-30 bg-black/30 backdrop-blur-sm md:hidden"
		onclick={closeDrawer}
		onkeydown={(e) => e.key === 'Escape' && closeDrawer()}
	></div>

	<nav class="fixed left-0 top-14 bottom-0 z-40 w-64 bg-surface-card border-r border-border md:hidden flex flex-col">
		<div class="flex-1 py-3 px-2 space-y-0.5">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm no-underline
						{isActive
							? 'bg-surface-alt text-text font-semibold'
							: 'text-text-muted hover:bg-surface-alt/50 hover:text-text'}"
					onclick={closeDrawer}
				>
					{section.label}
				</a>
			{/each}
		</div>

		<!-- Bottom attribution -->
		<div class="border-t border-border px-3 py-3 space-y-1">
			<div class="flex items-center gap-1.5 text-[11px] text-text-muted">
				<a href="https://www.eia.gov/" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">Data: EIA</a>
				<span class="text-text-muted/40">·</span>
				<a href="https://github.com/us-energy-data" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">GitHub</a>
			</div>
			<p class="text-[11px] text-text-muted/60">Updated weekly</p>
		</div>
	</nav>
{/if}
