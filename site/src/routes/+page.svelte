<svelte:head>
	<title>US Energy Data</title>
</svelte:head>

<script lang="ts">
	import { ENERGY_SOURCE_COLORS } from '$utils/colors';

	let { data } = $props();

	// Build generation mix from latest year
	const generationMix = $derived.by(() => {
		if (!data.generationData || data.generationData.length === 0) return [];
		const latestYear = Math.max(...data.generationData.map((d: any) => d.year));
		const latestData = data.generationData.filter((d: any) => d.year === latestYear);
		return latestData
			.map((d: any) => ({
				source: d.source,
				share: d.share,
				color: ENERGY_SOURCE_COLORS[d.source.toLowerCase()] ?? ENERGY_SOURCE_COLORS['other'],
			}))
			.sort((a: any, b: any) => b.share - a.share);
	});

	const sections = [
		{
			href: '/prices',
			title: 'Prices & Bills',
			desc: 'Retail electricity prices by sector, household bills, and regional comparisons.',
		},
		{
			href: '/demand',
			title: 'Electricity Demand',
			desc: 'Total consumption, per-capita demand, load growth, and trends by sector.',
		},
		{
			href: '/generation',
			title: 'Generation',
			desc: 'Electricity generation by source, carbon intensity, capacity, and storage.',
		},
		{
			href: '/fuels',
			title: 'Fossil Fuels',
			desc: 'Coal, oil, and natural gas production by state, consumption, imports and exports.',
		},
		{
			href: '/reliability',
			title: 'Reliability',
			desc: 'SAIDI trends, cross-state outage comparisons, and exploratory analysis.',
		},
	];
</script>

<!-- Hero -->
<div class="prose-width">
	<p
		class="font-mono text-xs uppercase tracking-[0.2em] text-accent animate-fade-up"
		style="--delay: 0s"
	>
		US Energy Data
	</p>
	<h1
		class="mt-4 text-[2.75rem] md:text-[3.5rem] font-serif leading-[1.1] tracking-tight text-text animate-fade-up"
		style="--delay: 0.08s"
	>
		Understanding<br />America's Energy System
	</h1>
	<div class="mt-6 w-16 h-px bg-accent animate-fade-up" style="--delay: 0.16s"></div>
	<p class="mt-6 narrative-text animate-fade-up" style="--delay: 0.24s">
		The United States generates over <span class="inline-stat">{data.stats.totalConsumption}</span> of electricity
		annually. Natural gas now accounts for roughly <span class="inline-stat">{data.stats.gasShare}</span> of
		generation, up from under 20% two decades ago. The average residential customer pays about
		<span class="inline-stat">{data.stats.avgResPrice}</span> per kilowatt-hour.
	</p>
</div>

<!-- Key stats strip -->
<div class="chart-breakout mt-10 animate-fade-up" style="--delay: 0.32s">
	<div class="flex flex-wrap gap-x-10 gap-y-4 py-5 border-y border-border">
		<div>
			<span class="font-mono text-2xl font-semibold text-text">{data.stats.totalConsumption}</span>
			<span class="block text-xs uppercase tracking-wider text-text-muted mt-1">{data.stats.consumptionLabel}</span>
		</div>
		<div>
			<span class="font-mono text-2xl font-semibold text-text">{data.stats.gasShare}</span>
			<span class="block text-xs uppercase tracking-wider text-text-muted mt-1">{data.stats.gasLabel}</span>
		</div>
		<div>
			<span class="font-mono text-2xl font-semibold text-text">{data.stats.avgResPrice}</span>
			<span class="block text-xs uppercase tracking-wider text-text-muted mt-1">{data.stats.priceLabel}</span>
		</div>
	</div>
</div>

<!-- Generation mix -->
{#if generationMix.length > 0}
	<div class="chart-breakout mt-12 animate-fade-up" style="--delay: 0.4s">
		<h2 class="section-heading" style="margin-top: 0;">Where does US electricity come from?</h2>
		<div class="flex h-10 w-full overflow-hidden rounded-sm mt-4">
			{#each generationMix as segment}
				<div
					class="h-full flex items-center justify-center transition-opacity duration-200"
					style="width: {segment.share}%; background: {segment.color};"
					title="{segment.source}: {segment.share.toFixed(1)}%"
				>
					{#if segment.share > 8}
						<span class="text-[11px] font-mono font-medium text-white/90 truncate px-1">
							{segment.share.toFixed(0)}%
						</span>
					{/if}
				</div>
			{/each}
		</div>
		<div class="mt-3 flex flex-wrap gap-x-4 gap-y-1.5 text-sm text-text-secondary">
			{#each generationMix as segment}
				<span class="flex items-center gap-1.5">
					<span class="inline-block h-2.5 w-2.5 rounded-sm" style="background: {segment.color}"></span>
					<span class="font-medium">{segment.source}</span>
					<span class="font-mono text-text-muted">{segment.share.toFixed(0)}%</span>
				</span>
			{/each}
		</div>
	</div>
{/if}

<!-- Explore the data -->
<div class="prose-width mt-16 animate-fade-up" style="--delay: 0.48s">
	<h2 class="section-heading" style="margin-top: 0;">Explore the data</h2>
</div>

<div class="chart-breakout mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
	{#each sections as section, i}
		<a
			href={section.href}
			class="group block p-5 rounded-lg border border-border hover:border-accent/40 hover:shadow-[var(--shadow-card-hover)] transition-all duration-200 animate-fade-up"
			style="--delay: {0.52 + i * 0.06}s"
		>
			<span class="text-lg font-serif text-text group-hover:text-accent transition-colors duration-200">
				{section.title}
			</span>
			<p class="mt-1.5 text-sm text-text-secondary leading-relaxed">
				{section.desc}
			</p>
			<span class="mt-3 inline-flex items-center gap-1 text-xs font-mono text-accent opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200">
				Explore <span aria-hidden="true">&rarr;</span>
			</span>
		</a>
	{/each}
</div>
