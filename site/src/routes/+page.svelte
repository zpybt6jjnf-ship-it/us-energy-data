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
				color: ENERGY_SOURCE_COLORS[d.source.toLowerCase()] ?? '#8892A4',
			}))
			.sort((a: any, b: any) => b.share - a.share);
	});

	// Build sparkline points for generation (total generation by year)
	const generationSparkline = $derived.by(() => {
		if (!data.generationData || data.generationData.length === 0) return '';
		const byYear = new Map<number, number>();
		for (const d of data.generationData) {
			byYear.set(d.year, (byYear.get(d.year) ?? 0) + d.generation);
		}
		const sorted = [...byYear.entries()].sort((a, b) => a[0] - b[0]);
		if (sorted.length === 0) return '';
		const minVal = Math.min(...sorted.map((d) => d[1]));
		const maxVal = Math.max(...sorted.map((d) => d[1]));
		const range = maxVal - minVal || 1;
		const points = sorted.map((d, i) => {
			const x = (i / (sorted.length - 1)) * 100;
			const y = 30 - ((d[1] - minVal) / range) * 28;
			return `${x},${y}`;
		});
		return points.join(' ');
	});

	// Build sparkline for prices (residential avg by year)
	const priceSparkline = $derived.by(() => {
		if (!data.priceData || data.priceData.length === 0) return '';
		const res = data.priceData.filter((d: any) => d.sector === 'Residential');
		const byYear = new Map<number, number>();
		for (const d of res) {
			byYear.set(d.year, d.price);
		}
		const sorted = [...byYear.entries()].sort((a, b) => a[0] - b[0]);
		if (sorted.length === 0) return '';
		const minVal = Math.min(...sorted.map((d) => d[1]));
		const maxVal = Math.max(...sorted.map((d) => d[1]));
		const range = maxVal - minVal || 1;
		const points = sorted.map((d, i) => {
			const x = (i / (sorted.length - 1)) * 100;
			const y = 30 - ((d[1] - minVal) / range) * 28;
			return `${x},${y}`;
		});
		return points.join(' ');
	});

	// Build sparkline for demand (total consumption by year)
	const demandSparkline = $derived.by(() => {
		if (!data.demandData || data.demandData.length === 0) return '';
		const byYear = new Map<number, number>();
		for (const d of data.demandData) {
			byYear.set(d.year, (byYear.get(d.year) ?? 0) + d.consumption);
		}
		const sorted = [...byYear.entries()].sort((a, b) => a[0] - b[0]);
		if (sorted.length === 0) return '';
		const minVal = Math.min(...sorted.map((d) => d[1]));
		const maxVal = Math.max(...sorted.map((d) => d[1]));
		const range = maxVal - minVal || 1;
		const points = sorted.map((d, i) => {
			const x = (i / (sorted.length - 1)) * 100;
			const y = 30 - ((d[1] - minVal) / range) * 28;
			return `${x},${y}`;
		});
		return points.join(' ');
	});

	// Build sparkline area path (closed polygon for fill)
	function sparklineArea(pointsStr: string): string {
		if (!pointsStr) return '';
		const pts = pointsStr.split(' ').map((p) => p.split(',').map(Number));
		if (pts.length === 0) return '';
		let d = `M0,30 L${pts[0][0]},${pts[0][1]}`;
		for (let i = 1; i < pts.length; i++) {
			d += ` L${pts[i][0]},${pts[i][1]}`;
		}
		d += ` L100,30 Z`;
		return d;
	}

	const sections = $derived([
		{
			href: '/prices',
			title: 'Prices & Bills',
			description: 'Retail electricity prices by sector, household bills, and regional comparisons.',
			color: '#5B8DEF',
			metric: data.stats.avgResPrice,
			metricLabel: 'avg residential',
			sparkline: priceSparkline,
		},
		{
			href: '/demand',
			title: 'Electricity Demand',
			description: 'Total consumption, per-capita demand, load growth, and trends by sector.',
			color: '#00E68A',
			metric: data.stats.totalConsumption,
			metricLabel: 'annual consumption',
			sparkline: demandSparkline,
		},
		{
			href: '/generation',
			title: 'Generation',
			description: 'Electricity generation by source, carbon intensity, capacity, and storage.',
			color: '#FBBF24',
			metric: data.stats.gasShare,
			metricLabel: 'natural gas share',
			sparkline: generationSparkline,
		},
		{
			href: '/fuels',
			title: 'Fossil Fuels',
			description: 'Coal, oil, and natural gas production by state, consumption, imports and exports.',
			color: '#FB923C',
			metric: null,
			metricLabel: '',
			sparkline: '',
		},
		{
			href: '/reliability',
			title: 'Reliability',
			description: 'SAIDI trends, cross-state outage comparisons, and exploratory analysis.',
			color: '#C084FC',
			metric: null,
			metricLabel: '',
			sparkline: '',
		},
	]);

	const stats = $derived([
		{ value: data.stats.avgResPrice, label: 'avg residential', sublabel: data.stats.priceLabel, color: '#5B8DEF' },
		{ value: data.stats.gasShare, label: 'natural gas', sublabel: data.stats.gasLabel, color: '#FBBF24' },
		{ value: data.stats.totalConsumption, label: 'annual TWh', sublabel: data.stats.consumptionLabel, color: '#00E68A' },
	]);
</script>

<!-- Hero header -->
<div class="relative pb-4 mb-4 border-b border-border">
	<!-- Ambient glow behind hero -->
	<div class="absolute -top-20 left-1/4 w-1/2 h-40 bg-accent/5 rounded-full blur-3xl pointer-events-none"></div>

	<div class="relative">
		<h1 class="text-4xl md:text-6xl font-display font-bold tracking-tighter text-text uppercase">
			US Energy <span class="text-accent">/</span> Data
		</h1>
		<span class="text-xs text-text-muted mt-1 block">Updated {new Date().toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}</span>
	</div>

	<!-- Gradient separator -->
	<div class="mt-3 h-px bg-gradient-to-r from-accent/40 via-accent/20 to-transparent"></div>
</div>

<!-- Compact stat strip -->
<div class="grid grid-cols-3 gap-2 mb-3">
	{#each stats as stat}
		<div class="flex items-baseline gap-2 rounded-md border border-border bg-surface-card px-3 py-2">
			<span class="text-lg font-bold font-mono glow-text" style="color: {stat.color}">{stat.value}</span>
			<span class="text-[11px] text-text-muted uppercase tracking-wide">{stat.label}</span>
		</div>
	{/each}
</div>

<!-- Generation mix bar (compact) -->
{#if generationMix.length > 0}
	<div class="mb-4">
		<div class="flex h-5 w-full overflow-hidden rounded">
			{#each generationMix as segment}
				<div
					class="h-full"
					style="width: {segment.share}%; background: {segment.color};"
					title="{segment.source}: {segment.share.toFixed(1)}%"
				></div>
			{/each}
		</div>
		<div class="mt-1.5 flex flex-wrap gap-3 text-[11px] text-text-secondary">
			{#each generationMix as segment}
				<span class="flex items-center gap-1">
					<span class="inline-block h-1.5 w-1.5 rounded-sm" style="background: {segment.color}"></span>
					{segment.source} {segment.share.toFixed(0)}%
				</span>
			{/each}
		</div>
	</div>
{/if}

<!-- Section card grid (2-col) -->
<div class="grid gap-3 lg:grid-cols-2">
	{#each sections as section}
		<a
			href={section.href}
			class="group flex flex-col rounded-lg border border-border bg-surface-card p-5 no-underline transition-all"
			style="border-top: 2px solid {section.color};"
			onmouseenter={(e) => { e.currentTarget.style.boxShadow = `0 0 24px ${section.color}15`; }}
			onmouseleave={(e) => { e.currentTarget.style.boxShadow = 'none'; }}
		>
			<div class="flex items-start justify-between gap-3">
				<div class="flex-1 min-w-0">
					<h2 class="text-sm font-semibold text-text">{section.title}</h2>
					<p class="mt-0.5 text-xs text-text-secondary leading-relaxed">{section.description}</p>
				</div>
				<span class="text-text-muted text-sm opacity-0 group-hover:opacity-100 transition-opacity shrink-0" aria-hidden="true">&rarr;</span>
			</div>

			{#if section.metric}
				<div class="mt-auto pt-2 flex items-end gap-2">
					<span class="text-lg font-bold font-mono glow-text" style="color: {section.color}">{section.metric}</span>
					<span class="text-[10px] uppercase tracking-wider text-text-muted pb-0.5">{section.metricLabel}</span>
				</div>
			{/if}

			{#if section.sparkline}
				<div class="mt-2 h-8 w-full opacity-50 group-hover:opacity-70 transition-opacity">
					<svg viewBox="0 0 100 30" class="w-full h-full" preserveAspectRatio="none">
						<path d={sparklineArea(section.sparkline)} fill="{section.color}" opacity="0.15" />
						<polyline points={section.sparkline} fill="none" stroke="{section.color}" stroke-width="1.5" vector-effect="non-scaling-stroke" />
					</svg>
				</div>
			{/if}
		</a>
	{/each}
</div>
