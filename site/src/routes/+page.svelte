<svelte:head>
	<title>US Energy Data</title>
</svelte:head>

<script lang="ts">
	let hoveredCard: string | null = $state(null);

	const sections = [
		{
			href: '/prices',
			title: 'Prices & Bills',
			description: 'Retail electricity prices by sector, household bills, and regional comparisons.',
			color: '#2166ac',
			iconId: 'prices',
		},
		{
			href: '/demand',
			title: 'Electricity Demand',
			description: 'Total consumption, per-capita demand, load growth, and trends by sector.',
			color: '#1b9e77',
			iconId: 'demand',
		},
		{
			href: '/generation',
			title: 'Generation & Resources',
			description: 'Electricity generation by source, carbon intensity, capacity, and storage.',
			color: '#e7a02f',
			iconId: 'generation',
		},
		{
			href: '/fuels',
			title: 'Fossil Fuels',
			description: 'Coal, oil, and natural gas production by state, consumption, imports and exports.',
			color: '#a6611a',
			iconId: 'fuels',
		},
		{
			href: '/reliability',
			title: 'Reliability & Outages',
			description: 'SAIDI trends, cross-state outage comparisons, and exploratory analysis.',
			color: '#984ea3',
			iconId: 'reliability',
		},
	];

	const stats = [
		{ value: '17.4¢', label: 'avg. residential electricity price (2024)' },
		{ value: '43%', label: 'of electricity from natural gas' },
		{ value: '4.1T kWh', label: 'annual electricity consumption' },
	];
</script>

<!-- Hero section -->
<div class="py-16 sm:py-20">
	<h1
		class="text-5xl sm:text-6xl text-text leading-tight"
		style="font-family: var(--font-display)"
	>
		Understanding America's Energy
	</h1>
	<p class="mt-5 max-w-2xl text-lg text-text-secondary leading-relaxed">
		Explore electricity prices, demand, generation, and fossil fuel production through interactive
		charts and maps — built with data from the US Energy Information Administration.
	</p>

	<!-- Highlight stats -->
	<div class="mt-10 flex flex-wrap gap-8 sm:gap-12">
		{#each stats as stat}
			<div class="flex flex-col">
				<span class="text-4xl font-bold text-accent">{stat.value}</span>
				<span class="mt-1 text-sm text-text-muted">{stat.label}</span>
			</div>
		{/each}
	</div>
</div>

<!-- Section cards -->
<div class="mt-16">
	<p class="text-sm font-semibold uppercase tracking-wider text-text-muted">Explore the data</p>

	<div class="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
		{#each sections as section}
			<a
				href={section.href}
				class="group relative flex flex-col rounded-xl border border-border bg-surface-card p-6 no-underline transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg"
				style="border-left: 4px solid {section.color}"
				onmouseenter={() => (hoveredCard = section.iconId)}
				onmouseleave={() => (hoveredCard = null)}
			>
				<!-- Icon -->
				<div class="mb-3" style="color: {section.color}">
					{#if section.iconId === 'prices'}
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<line x1="12" y1="1" x2="12" y2="23" />
							<path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
						</svg>
					{:else if section.iconId === 'demand'}
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
							<path d="M13 2L3 14h9l-1 10 10-12h-9l1-10z" />
						</svg>
					{:else if section.iconId === 'generation'}
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
							<rect x="2" y="14" width="4" height="8" rx="1" />
							<rect x="8" y="8" width="4" height="14" rx="1" />
							<rect x="14" y="4" width="4" height="18" rx="1" />
							<rect x="20" y="10" width="2" height="12" rx="0.5" />
						</svg>
					{:else if section.iconId === 'fuels'}
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
							<path d="M12 2c-4 6-8 9.5-8 13a8 8 0 0016 0c0-3.5-4-7-8-13z" />
						</svg>
					{:else if section.iconId === 'reliability'}
						<svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
							<polyline points="9 12 11 14 15 10" />
						</svg>
					{/if}
				</div>

				<!-- Content -->
				<h2 class="text-lg font-semibold text-text">
					{section.title}
				</h2>
				<p class="mt-1 text-sm text-text-secondary leading-relaxed">
					{section.description}
				</p>

				<!-- Arrow indicator -->
				<span
					class="absolute right-4 top-1/2 -translate-y-1/2 text-text-muted opacity-0 transition-opacity duration-200 group-hover:opacity-100"
					aria-hidden="true"
				>
					&rarr;
				</span>
			</a>
		{/each}
	</div>
</div>
