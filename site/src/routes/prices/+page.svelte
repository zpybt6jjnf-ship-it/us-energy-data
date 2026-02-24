<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import MapChartToggle from '$components/charts/MapChartToggle.svelte';
	import YearSlider from '$components/ui/YearSlider.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { chartConfig, updateConfig, toggleState, hasActiveFilters, resetConfig } from '$stores/chartConfig';
	import { stateFips, stateFromAbbr } from '$utils/states';
	import { CHART_COLORS_CSS, BILLS_COLORS } from '$utils/colors';
	import { interpolateYlOrRd } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const priceAnnotations = [
		{ date: 2009, label: '08–09 Recession' },
		{ date: 2020, label: 'COVID-19', labelPosition: 'bottom' as const },
		{ date: 2022, label: 'IRA' },
	];

	const sectorOptions = [
		{ value: 'all', label: 'All Sectors' },
		{ value: 'residential', label: 'Residential' },
		{ value: 'commercial', label: 'Commercial' },
		{ value: 'industrial', label: 'Industrial' },
	];

	// Build series from real data
	const allSeries: DataSeries[] = $derived((() => {
		const sectors = [...new Set(data.national.map((d: any) => d.sector))] as string[];
		return sectors.map((sector) => ({
			name: sector,
			values: data.national
				.filter((d: any) => d.sector === sector)
				.map((d: any) => ({ date: d.year, value: d.price }))
				.sort((a: any, b: any) => a.date - b.date),
		}));
	})());

	const activeSector = $derived(
		$chartConfig.sector === 'residential' || $chartConfig.sector === 'commercial' || $chartConfig.sector === 'industrial'
			? $chartConfig.sector
			: 'all'
	);

	const filteredSeries = $derived(
		activeSector === 'all'
			? allSeries
			: allSeries.filter((s) => s.name.toLowerCase() === activeSector)
	);

	// State comparison: build state-level series for selected states
	const selectedStates = $derived($chartConfig.states);

	const sectorForState = $derived(
		activeSector === 'all' ? 'residential' : activeSector
	);

	const stateSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);
			const sectorLabel = sectorForState.charAt(0).toUpperCase() + sectorForState.slice(1);
			return {
				name: `${abbr} (${sectorLabel})`,
				color: CHART_COLORS_CSS[(filteredSeries.length + i) % CHART_COLORS_CSS.length],
				values: data.byState
					.filter((d: any) => d.state === fullName && d.sector === sectorLabel)
					.map((d: any) => ({ date: d.year, value: d.price }))
					.sort((a: any, b: any) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const combinedSeries = $derived([...filteredSeries, ...stateSeries]);

	const startYear = $derived($chartConfig.startYear);
	const endYear = $derived($chartConfig.endYear);

	const timeFilteredSeries = $derived(
		combinedSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const lineMeta: ChartMeta = {
		title: 'Retail Electricity Prices by Sector',
		subtitle: 'US national average, cents per kilowatt-hour, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'cents/kWh',
		lastUpdated: data.lastUpdated,
		description: 'Average retail electricity prices vary significantly across sectors. Residential customers typically pay the highest rates due to distribution costs, while industrial users benefit from bulk pricing and direct market access. Use the state selector to compare individual states against the national average.',
		caveats: 'Prices are nominal (not adjusted for inflation). National averages are revenue-weighted across all utilities. Some state-level data may be incomplete for earlier years.',
		relatedCharts: [
			{ title: 'Generation mix by state', href: '/generation#generation-mix' },
			{ title: 'Demand trends', href: '/demand' },
		],
	};

	// State-level map data
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	// Available years for map slider
	const mapAvailableYears = $derived(
		[...new Set<number>(data.byState.filter((d: any) => d.sector === 'Residential').map((d: any) => d.year as number))].sort((a, b) => a - b)
	);
	let mapYear = $state(0); // Will be initialized by effect
	$effect(() => { if (mapYear === 0 && latestYear > 0) mapYear = latestYear; });

	// Map/chart toggle
	let mapMode = $state<'map' | 'chart'>('map');

	// Key figures
	const latestRes = $derived(data.national.filter((d: any) => d.year === latestYear && d.sector === 'Residential'));
	const latestInd = $derived(data.national.filter((d: any) => d.year === latestYear && d.sector === 'Industrial'));
	const resPrice = $derived(latestRes.length > 0 ? latestRes[0].price : 0);
	const indPrice = $derived(latestInd.length > 0 ? latestInd[0].price : 0);
	const sectorGap = $derived(indPrice > 0 ? Math.round(((resPrice - indPrice) / indPrice) * 100) : 0);

	const mapData = $derived(
		data.byState
			.filter((d: any) => d.year === mapYear && d.sector === 'Residential')
			.map((d: any) => ({
				state: d.state as string,
				fips: stateFips(d.state),
				value: d.price as number,
			}))
			.filter((d: { fips: string | undefined; }) => d.fips)
	);

	// Bar chart data for map/chart toggle (sorted by value)
	const mapBarData = $derived(
		[...mapData]
			.sort((a, b) => (b.value as number) - (a.value as number))
			.slice(0, 15)
			.map((d) => ({
				label: d.state,
				value: d.value,
			}))
	);

	const mapMeta: ChartMeta = $derived({
		title: `Residential Electricity Prices by State (${mapYear})`,
		subtitle: 'Cents per kilowatt-hour',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'cents/kWh',
		lastUpdated: data.lastUpdated,
		description: 'Electricity prices vary widely across states, driven by differences in fuel mix, regulatory environment, and infrastructure costs. States with abundant hydropower (e.g., Washington) tend to have the lowest rates, while island states (Hawaii) and those with older infrastructure pay the most.',
		caveats: 'Residential prices only. Commercial and industrial rates follow different patterns. Colors use a yellow-to-red scale where yellow indicates lower prices.',
		relatedCharts: [
			{ title: 'Renewable share by state', href: '/generation#generation-mix' },
			{ title: 'Per-capita consumption', href: '/demand' },
		],
	});

	function colorInterp(t: number): string {
		return interpolateYlOrRd(t);
	}

	// Market structure map (state name → ISO/RTO)
	const marketMap = $derived(new Map<string, string>(
		data.marketStructure.map((d: any) => [d.state, d.market])
	));

	// Scatter: Prices vs Renewable Share by state
	const priceVsMixData = $derived((() => {
		const priceMap = new Map<string, number>();
		for (const d of data.byState) {
			if (d.year === latestYear && d.sector === 'Residential') {
				priceMap.set(d.state, d.price);
			}
		}
		const renewMap = new Map<string, number>();
		for (const d of data.renewableShare) {
			renewMap.set(d.state, d.renewable_share);
		}
		return [...priceMap.entries()]
			.filter(([state]) => renewMap.has(state))
			.map(([state, price]) => ({
				x: renewMap.get(state)!,
				y: price,
				label: state,
				group: marketMap.get(state) ?? 'Non-ISO',
			}));
	})());

	const scatterMeta: ChartMeta = $derived({
		title: `Electricity Price vs Renewable Share by State (${latestYear})`,
		subtitle: 'Each dot is a state',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '',
		lastUpdated: data.lastUpdated,
		description: 'Is there a relationship between renewable energy adoption and electricity prices? This scatter plot shows each state\'s residential electricity price against its renewable generation share. The relationship is complex — states with cheap hydro tend to have both high renewables and low prices, while other factors like grid infrastructure and regulation also play major roles.',
		caveats: 'Correlation does not imply causation. States with high renewable shares include those with abundant hydropower (historically cheap) and those with newer wind/solar capacity (varying cost impact). Residential prices reflect many factors beyond generation mix.',
	});

	// Household electricity bills series
	const billsSeries: DataSeries[] = $derived([
		{
			name: 'Nominal',
			color: BILLS_COLORS.nominal,
			values: data.bills
				.map((d: any) => ({ date: d.year, value: d.nominal_bill }))
				.sort((a: any, b: any) => a.date - b.date),
		},
		{
			name: 'Real (2024$)',
			color: BILLS_COLORS.real,
			values: data.bills
				.filter((d: any) => d.real_bill != null)
				.map((d: any) => ({ date: d.year, value: d.real_bill }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const timeFilteredBills = $derived(
		billsSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const billsMeta: ChartMeta = {
		title: 'Average Monthly Household Electricity Bill',
		subtitle: 'Dollars per month',
		source: 'US Energy Information Administration + CPI-U',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '$',
		lastUpdated: data.lastUpdated,
		description: 'Electricity bills have risen in nominal terms but the increase is more modest after adjusting for inflation. The average US household consumes about 900 kWh per month.',
		caveats: 'Bills estimated as average residential price × 900 kWh/month. Real values adjusted to 2024 dollars using CPI-U.',
	};
</script>

<svelte:head>
	<title>Prices & Bills — US Energy Data</title>
</svelte:head>

<div>
	<!-- Title + intro -->
	<div class="prose-width">
		<h1 class="text-2xl font-display font-semibold tracking-tight text-text">Prices & Bills</h1>
		<p class="mt-3 text-text-secondary leading-relaxed">
			Electricity prices in the US vary widely — by sector, by state, and over time.
			In {latestYear}, residential customers paid an average of
			<span class="inline-stat">{resPrice.toFixed(1)}&cent;/kWh</span>, roughly
			<span class="inline-stat">{sectorGap}%</span> more than industrial users at
			<span class="inline-stat">{indPrice.toFixed(1)}&cent;/kWh</span>.
		</p>
	</div>

	<!-- Section: Price trends over time -->
	<div class="prose-width">
		<h2 class="section-heading">How have prices changed over time?</h2>
		<p class="mt-2 text-text-secondary leading-relaxed">
			National electricity prices have risen steadily in nominal terms, shaped by recessions, policy shifts, and fuel costs. The gap between residential and industrial rates reflects differences in distribution costs and market access.
		</p>
	</div>

	<section class="chart-breakout mt-6">
		<ChartWrapper meta={lineMeta} data={timeFilteredSeries.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, price: v.value })))}>
			{#snippet controls()}
				<Dropdown
					options={sectorOptions}
					value={activeSector}
					label="Sector"
					onchange={(v) => updateConfig('sector', v)}
				/>
				<StateSelect
					selected={selectedStates}
					onchange={(states) => updateConfig('state', states)}
					label=""
					compact
				/>
				<TimeRangeSlider {startYear} {endYear} />
				{#if hasActiveFilters($chartConfig)}
					<button onclick={resetConfig} class="text-xs text-text-muted hover:text-accent transition-colors">Reset</button>
				{/if}
			{/snippet}
			<LineChart
				series={timeFilteredSeries}
				xLabel="Year"
				yLabel="cents/kWh"
				yFormat={format(',.1f')}
				unit="cents/kWh"
				annotations={priceAnnotations}
				showTrend={3}
			/>
		</ChartWrapper>
	</section>

	<!-- Insight card -->
	<div class="prose-width mt-6 insight-card">
		<div class="flex items-start gap-4">
			<div class="flex-shrink-0">
				<span class="text-xl font-bold text-accent" style="font-family: var(--font-mono)">{sectorGap}%</span>
				<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">price gap</span>
			</div>
			<p class="text-sm leading-relaxed text-text-secondary">
				Residential customers pay roughly {sectorGap}% more per kWh than industrial users — a gap that has widened over the past decade.
			</p>
		</div>
	</div>

	<!-- Section: State variation -->
	<div class="prose-width mt-12">
		<h2 class="section-heading">How do prices vary across states?</h2>
		<p class="mt-2 text-text-secondary leading-relaxed">
			Geography matters. States with abundant hydropower like Washington enjoy rates well below the national average, while Hawaii and parts of New England pay the most. Fuel mix, regulation, and infrastructure age all play a role.
		</p>
	</div>

	<section class="chart-breakout mt-6">
		<ChartWrapper meta={mapMeta} data={mapData.map((d: any) => ({ state: d.state, price: d.value }))}>
			{#snippet controls()}
				<MapChartToggle mode={mapMode} onToggle={(m) => { mapMode = m; }} />
				{#if mapAvailableYears.length > 1}
					<div class="flex-1 min-w-[200px] max-w-[400px]">
						<YearSlider min={mapAvailableYears[0]} max={mapAvailableYears[mapAvailableYears.length - 1]} value={mapYear} onchange={(y) => { mapYear = y; }} />
					</div>
				{/if}
			{/snippet}
			{#if mapMode === 'map'}
				<ChoroplethMap
					data={mapData}
					topology={data.topology}
					colorInterpolator={colorInterp}
					valueFormat={format(',.1f')}
					unit="cents/kWh"
					onStateClick={toggleState}
				/>
			{:else}
				<BarChart
					data={mapBarData}
					horizontal
					yFormat={format(',.1f')}
					unit="cents/kWh"
					margin={{ top: 20, right: 20, bottom: 60, left: 120 }}
				/>
			{/if}
		</ChartWrapper>
		{#if selectedStates.length > 0}
			<p class="text-xs text-text-muted mt-1">Shows all states — click a state to add it to the line chart filter</p>
		{/if}
	</section>

	<!-- Section: Renewables and prices -->
	<div class="prose-width mt-12">
		<h2 class="section-heading">Do renewables make electricity cheaper or more expensive?</h2>
		<p class="mt-2 text-text-secondary leading-relaxed">
			The relationship between renewable energy and electricity prices is not straightforward. States with cheap hydropower tend to have both high renewable shares and low prices, but other factors — grid age, regulatory structure, and demand patterns — matter just as much.
		</p>
	</div>

	<div class="chart-breakout mt-6 grid md:grid-cols-2 gap-3">
		<section>
			<ChartWrapper meta={scatterMeta} data={priceVsMixData.map((d) => ({ state: d.label, renewable_share: d.x, price: d.y }))}>
				<Scatter
					data={priceVsMixData}
					xLabel="Renewable share (%)"
					yLabel="Residential price (cents/kWh)"
					xFormat={format(',.0f')}
					yFormat={format(',.1f')}
					unit="cents/kWh"
				/>
			</ChartWrapper>
		</section>

		<section>
			<ChartWrapper meta={billsMeta} data={timeFilteredBills.flatMap((s) => s.values.map((v) => ({ year: v.date, [s.name === 'Nominal' ? 'nominal_bill' : 'real_bill']: v.value })))}>
				<LineChart
					series={timeFilteredBills}
					xLabel="Year"
					yLabel="$/month"
					yFormat={format('$,.0f')}
					unit="$"
				/>
			</ChartWrapper>
		</section>
	</div>

	<!-- Cross-link -->
	<p class="prose-width mt-8">
		<a href="/generation" class="text-accent hover:text-accent-light no-underline font-medium">How do these states generate their electricity? &rarr;</a>
	</p>
</div>
