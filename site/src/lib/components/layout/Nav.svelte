<script lang="ts">
	import { page } from '$app/stores';

	const sections = [
		{ href: '/prices', label: 'Prices & Bills', color: '#2166ac' },
		{ href: '/demand', label: 'Demand', color: '#1b9e77' },
		{ href: '/generation', label: 'Generation', color: '#e7a02f' },
		{ href: '/fuels', label: 'Fuels', color: '#a6611a' },
		{ href: '/reliability', label: 'Reliability', color: '#984ea3' },
	];

	let drawerOpen = $state(false);

	function closeDrawer() {
		drawerOpen = false;
	}
</script>

<!-- Top bar -->
<header class="fixed top-0 left-0 right-0 z-40 h-12 bg-surface-card border-b border-border flex items-center px-4">
	<a href="/" class="flex items-center gap-2 text-sm font-semibold text-text no-underline hover:text-text/80" onclick={closeDrawer}>
		<svg class="h-4 w-4 text-accent" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
			<polygon points="11,1 5,11 9,11 7,19 15,9 11,9 13,1" />
		</svg>
		US Energy Data
	</a>

	<!-- Mobile hamburger -->
	<button
		class="ml-auto rounded-md p-2 text-text-secondary hover:bg-surface-alt hover:text-text md:hidden"
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
</header>

<!-- Desktop sidebar -->
<nav class="hidden md:flex md:flex-col md:fixed md:left-0 md:top-12 md:bottom-0 md:w-48 md:bg-surface-card md:border-r md:border-border md:z-30">
	<div class="flex-1 py-3 px-2 space-y-0.5">
		{#each sections as section}
			{@const isActive = $page.url.pathname.startsWith(section.href)}
			<a
				href={section.href}
				class="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm no-underline
					{isActive
						? 'bg-surface-alt text-text font-medium border-l-[3px] -ml-[3px]'
						: 'text-text-secondary hover:bg-surface-alt/50 hover:text-text'}"
				style={isActive ? `border-left-color: ${section.color}` : ''}
			>
				<span class="h-1 w-1 rounded-full shrink-0" style="background-color: {section.color}"></span>
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

<!-- Mobile drawer overlay -->
{#if drawerOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		class="fixed inset-0 z-30 bg-black/20 md:hidden"
		onclick={closeDrawer}
		onkeydown={(e) => e.key === 'Escape' && closeDrawer()}
	></div>

	<nav class="fixed left-0 top-12 bottom-0 z-40 w-64 bg-surface-card shadow-lg border-r border-border md:hidden flex flex-col">
		<div class="flex-1 py-3 px-2 space-y-0.5">
			{#each sections as section}
				{@const isActive = $page.url.pathname.startsWith(section.href)}
				<a
					href={section.href}
					class="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm no-underline
						{isActive
							? 'bg-surface-alt text-text font-medium border-l-[3px] -ml-[3px]'
							: 'text-text-secondary hover:bg-surface-alt/50 hover:text-text'}"
					style={isActive ? `border-left-color: ${section.color}` : ''}
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
				<a href="https://www.eia.gov/" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">Data: EIA</a>
				<span class="text-text-muted/40">·</span>
				<a href="https://github.com/us-energy-data" target="_blank" rel="noopener noreferrer" class="text-text-muted no-underline hover:text-text-secondary">GitHub</a>
			</div>
			<p class="text-[11px] text-text-muted/60">Updated weekly</p>
		</div>
	</nav>
{/if}
