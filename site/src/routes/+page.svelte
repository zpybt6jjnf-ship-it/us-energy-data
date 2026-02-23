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
</script>

<!-- Title -->
<div class="prose-width">
	<h1 class="text-3xl md:text-4xl font-display tracking-tight text-text">
		Understanding America's Energy System
	</h1>
</div>

<!-- Intro paragraph with inline stats -->
<div class="prose-width mt-4">
	<p class="narrative-text">
		The United States generates over <span class="inline-stat">{data.stats.totalConsumption}</span> of electricity
		annually. Natural gas now accounts for roughly <span class="inline-stat">{data.stats.gasShare}</span> of
		generation, up from under 20% two decades ago. The average residential customer pays about
		<span class="inline-stat">{data.stats.avgResPrice}</span> per kilowatt-hour.
	</p>
</div>

<!-- Generation mix bar -->
{#if generationMix.length > 0}
	<div class="chart-breakout mt-8">
		<h2 class="section-heading" style="margin-top: 0;">Where does US electricity come from?</h2>
		<div class="flex h-6 w-full overflow-hidden rounded">
			{#each generationMix as segment}
				<div
					class="h-full"
					style="width: {segment.share}%; background: {segment.color};"
					title="{segment.source}: {segment.share.toFixed(1)}%"
				></div>
			{/each}
		</div>
		<div class="mt-2 flex flex-wrap gap-3 text-sm text-text-secondary">
			{#each generationMix as segment}
				<span class="flex items-center gap-1.5">
					<span class="inline-block h-2 w-2 rounded-sm" style="background: {segment.color}"></span>
					{segment.source} {segment.share.toFixed(0)}%
				</span>
			{/each}
		</div>
	</div>
{/if}

<!-- Explore the data -->
<div class="prose-width">
	<h2 class="section-heading">Explore the data</h2>
	<ul class="space-y-4 mt-4">
		<li>
			<a href="/prices" class="text-accent hover:text-accent-light no-underline font-medium">Prices & Bills</a>
			<p class="narrative-text mt-0.5">Retail electricity prices by sector, household bills, and regional comparisons.</p>
		</li>
		<li>
			<a href="/demand" class="text-accent hover:text-accent-light no-underline font-medium">Electricity Demand</a>
			<p class="narrative-text mt-0.5">Total consumption, per-capita demand, load growth, and trends by sector.</p>
		</li>
		<li>
			<a href="/generation" class="text-accent hover:text-accent-light no-underline font-medium">Generation</a>
			<p class="narrative-text mt-0.5">Electricity generation by source, carbon intensity, capacity, and storage.</p>
		</li>
		<li>
			<a href="/fuels" class="text-accent hover:text-accent-light no-underline font-medium">Fossil Fuels</a>
			<p class="narrative-text mt-0.5">Coal, oil, and natural gas production by state, consumption, imports and exports.</p>
		</li>
		<li>
			<a href="/reliability" class="text-accent hover:text-accent-light no-underline font-medium">Reliability</a>
			<p class="narrative-text mt-0.5">SAIDI trends, cross-state outage comparisons, and exploratory analysis.</p>
		</li>
	</ul>
</div>
