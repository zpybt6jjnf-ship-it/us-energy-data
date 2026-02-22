<svelte:head>
	<title>US Energy Data</title>
</svelte:head>

<script lang="ts">
	import { ENERGY_SOURCE_COLORS } from '$utils/colors';

	let { data } = $props();

	let hoveredCard: string | null = $state(null);

	// Build generation mix from latest year
	const generationMix = $derived.by(() => {
		if (!data.generationData || data.generationData.length === 0) return [];
		const latestYear = Math.max(...data.generationData.map((d: any) => d.year));
		const latestData = data.generationData.filter((d: any) => d.year === latestYear);
		// Sort by share descending so largest segments come first
		return latestData
			.map((d: any) => ({
				source: d.source,
				share: d.share,
				color: ENERGY_SOURCE_COLORS[d.source.toLowerCase()] ?? '#999999',
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
			color: '#2166ac',
			iconId: 'prices',
			metric: data.stats.avgResPrice,
			metricLabel: 'avg residential',
			sparkline: priceSparkline,
		},
		{
			href: '/demand',
			title: 'Electricity Demand',
			description: 'Total consumption, per-capita demand, load growth, and trends by sector.',
			color: '#1b9e77',
			iconId: 'demand',
			metric: data.stats.totalConsumption,
			metricLabel: 'annual consumption',
			sparkline: demandSparkline,
		},
		{
			href: '/generation',
			title: 'Generation & Resources',
			description: 'Electricity generation by source, carbon intensity, capacity, and storage.',
			color: '#e7a02f',
			iconId: 'generation',
			metric: data.stats.gasShare,
			metricLabel: 'natural gas share',
			sparkline: generationSparkline,
		},
		{
			href: '/fuels',
			title: 'Fossil Fuels',
			description: 'Coal, oil, and natural gas production by state, consumption, imports and exports.',
			color: '#a6611a',
			iconId: 'fuels',
			metric: null,
			metricLabel: '',
			sparkline: '',
		},
		{
			href: '/reliability',
			title: 'Reliability & Outages',
			description: 'SAIDI trends, cross-state outage comparisons, and exploratory analysis.',
			color: '#984ea3',
			iconId: 'reliability',
			metric: null,
			metricLabel: '',
			sparkline: '',
		},
	]);

	const stats = $derived([
		{ value: data.stats.avgResPrice, topLabel: 'Avg. Residential Price', label: data.stats.priceLabel, color: '#2166ac' },
		{ value: data.stats.gasShare, topLabel: 'Natural Gas Share', label: data.stats.gasLabel, color: '#e7a02f' },
		{ value: data.stats.totalConsumption, topLabel: 'Annual Consumption', label: data.stats.consumptionLabel, color: '#1b9e77' },
	]);

	// Stat counter animation
	let statsEl: HTMLDivElement | undefined = $state();
	let statsVisible = $state(false);
	let animProgress = $state(0);

	$effect(() => {
		if (!statsEl) return;
		const io = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting) {
					statsVisible = true;
					io.disconnect();
				}
			},
			{ threshold: 0.3 }
		);
		io.observe(statsEl);
		return () => io.disconnect();
	});

	$effect(() => {
		if (!statsVisible) return;
		const duration = 1500;
		const start = performance.now();
		function tick(now: number) {
			const t = Math.min((now - start) / duration, 1);
			animProgress = 1 - Math.pow(1 - t, 3); // ease-out cubic
			if (t < 1) requestAnimationFrame(tick);
		}
		requestAnimationFrame(tick);
	});

	function animateStat(raw: string, progress: number): string {
		// Parse number and suffix from stat string like "17.4c" or "43%" or "3.9T"
		const match = raw.match(/^([\d,.]+)(.*)$/);
		if (!match) return raw;
		const num = parseFloat(match[1].replace(/,/g, ''));
		const suffix = match[2];
		const current = num * progress;
		// Preserve decimal places from original
		const decimals = match[1].includes('.') ? match[1].split('.')[1].replace(/[^\d]/g, '').length : 0;
		const formatted = current.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
		return formatted + suffix;
	}
</script>

<!-- Hero section -->
<div class="hero-gradient noise-overlay py-20 sm:py-28">
	<h1
		class="text-5xl sm:text-7xl text-text leading-tight"
		style="font-family: var(--font-display)"
	>
		Explore U.S. Energy Data
	</h1>

	<!-- Animated accent line -->
	<div class="mt-5 h-1 w-24 rounded-full animated-accent-line"></div>

	<p class="mt-6 max-w-2xl text-lg text-text-secondary leading-relaxed">
		Interactive charts and maps covering electricity prices, demand, generation, and fossil fuels — powered by EIA data.
	</p>

	<!-- Dashboard-style stat cards -->
	<div class="mt-12 grid grid-cols-1 gap-4 sm:grid-cols-3" bind:this={statsEl}>
		{#each stats as stat, i}
			<div class="stat-card" style="border-bottom: 3px solid {stat.color};">
				<span class="text-[11px] font-medium uppercase tracking-wider text-text-muted">{stat.topLabel}</span>
				<span class="text-4xl sm:text-5xl font-bold text-accent" style="font-family: var(--font-mono)">
					{animateStat(stat.value, animProgress)}
				</span>
				<span class="text-xs text-text-secondary">{stat.label}</span>
			</div>
		{/each}
	</div>

	<!-- Generation mix bar -->
	{#if generationMix.length > 0}
		<div class="mt-16 mb-4">
			<p class="text-sm font-semibold text-text-secondary mb-3">How America generates electricity</p>
			<div class="flex h-8 w-full overflow-hidden rounded-lg">
				{#each generationMix as segment}
					<div
						class="h-full transition-all duration-700"
						style="width: {segment.share}%; background: {segment.color};"
						title="{segment.source}: {segment.share.toFixed(1)}%"
					></div>
				{/each}
			</div>
			<div class="mt-2 flex flex-wrap gap-3 text-xs text-text-secondary">
				{#each generationMix as segment}
					<span class="flex items-center gap-1">
						<span class="inline-block h-2 w-2 rounded-sm" style="background: {segment.color}"></span>
						{segment.source} {segment.share.toFixed(0)}%
					</span>
				{/each}
			</div>
		</div>
	{/if}
</div>

<!-- Section cards -->
<div class="mt-20">
	<div class="section-divider"></div>
	<h2 class="mt-8 text-2xl font-bold text-text" style="font-family: var(--font-display)">Explore the data</h2>
	<p class="mt-1 text-sm text-text-secondary">Five perspectives on the American energy system</p>

	<div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each sections as section, i}
			<a
				href={section.href}
				class="group relative flex flex-col rounded-xl border border-border bg-surface-card p-6 no-underline transition-all duration-300 hover:-translate-y-1 hover:shadow-xl {i === 0 ? 'sm:col-span-2 lg:col-span-2' : ''}"
				style="border-top: 3px solid {section.color}; animation: cardEntrance 0.5s ease-out {i * 50}ms both;"
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

				<!-- Metric -->
				{#if section.metric}
					<span class="mt-auto pt-3 text-2xl font-bold" style="font-family: var(--font-mono); color: {section.color}">
						{section.metric}
					</span>
					<span class="text-[10px] uppercase tracking-wider text-text-muted">{section.metricLabel}</span>
				{/if}

				<!-- Sparkline -->
				{#if section.sparkline}
					<div class="mt-3 h-10 w-full opacity-60 group-hover:opacity-80 transition-opacity">
						<svg viewBox="0 0 100 30" class="w-full h-full" preserveAspectRatio="none">
							<path d={sparklineArea(section.sparkline)} fill="{section.color}" opacity="0.2" />
							<polyline points={section.sparkline} fill="none" stroke="{section.color}" stroke-width="1.5" vector-effect="non-scaling-stroke" />
						</svg>
					</div>
				{:else}
					<!-- Decorative gradient bar for cards without sparkline data -->
					<div class="mt-auto pt-4">
						<div class="h-1 w-full rounded-full opacity-20" style="background: linear-gradient(90deg, {section.color}, transparent);"></div>
					</div>
				{/if}

				<!-- Arrow indicator -->
				<span
					class="absolute right-4 top-6 text-text-muted opacity-0 transition-opacity duration-200 group-hover:opacity-100"
					aria-hidden="true"
				>
					&rarr;
				</span>
			</a>
		{/each}
	</div>
</div>

<style>
	.animated-accent-line {
		background: linear-gradient(90deg, var(--color-accent), var(--color-primary), var(--color-accent));
		background-size: 200% 100%;
		animation: accent-shift 4s ease-in-out infinite;
	}

	@keyframes accent-shift {
		0%, 100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	@keyframes cardEntrance {
		from {
			opacity: 0;
			transform: translateY(16px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
