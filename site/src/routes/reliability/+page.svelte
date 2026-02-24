<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import MapChartToggle from '$components/charts/MapChartToggle.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import { chartConfig, updateConfig, toggleState, hasActiveFilters, resetConfig } from '$stores/chartConfig';
	import { stateFromAbbr } from '$utils/states';
	import { CHART_COLORS_CSS } from '$utils/colors';
	import { format } from 'd3-format';
	import { interpolateYlOrRd } from 'd3-scale-chromatic';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	// --- Controls ---
	const medOptions = [
		{ value: 'with_med', label: 'With Major Event Days' },
		{ value: 'without_med', label: 'Without Major Event Days' },
	];

	const activeMed = $derived(
		$chartConfig.med === 'without_med' ? 'without_med' : 'with_med'
	);

	// --- Chart 1: National SAIDI trend ---
	const saidiField = $derived(activeMed === 'without_med' ? 'saidi_no_med' : 'saidi');
	const saifiField = $derived(activeMed === 'without_med' ? 'saifi_no_med' : 'saifi');

	const saidiSeries: DataSeries[] = $derived([
		{
			name: 'SAIDI (avg. interruption minutes)',
			values: data.national.map((d: any) => ({
				date: d.year,
				value: d[saidiField],
			})),
		},
	]);

	const saidiAnnotations = [
		{ date: 2017, label: 'Harvey/Irma' },
		{ date: 2020, label: 'Derecho' },
		{ date: 2021, label: 'Winter Storm Uri' },
		{ date: 2024, label: 'Helene/Milton' },
	];

	const lineMeta: ChartMeta = $derived({
		title: 'Average Power Outage Duration Over Time',
		subtitle: activeMed === 'without_med'
			? 'SAIDI excluding major event days, US customer-weighted average'
			: 'System Average Interruption Duration Index (SAIDI), US customer-weighted average',
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: 'minutes/customer/year',
		lastUpdated: data.lastUpdated,
		description: 'SAIDI measures the average total duration of power interruptions per customer per year, weighted by number of customers served. Data aggregated from ~950 utility reports filed annually with the EIA.',
		caveats: activeMed === 'with_med'
			? 'Including major event days (hurricanes, ice storms, etc.) causes large year-to-year variation. Toggle to "Without Major Event Days" for a steadier trend.'
			: 'Excluding major event days removes the impact of catastrophic weather events (hurricanes, ice storms) to show underlying grid reliability trends.',
		relatedCharts: [
			{ title: 'Prices by state', href: '/prices' },
			{ title: 'Generation mix', href: '/generation#generation-mix' },
		],
	});

	// --- State comparison overlay on SAIDI trend ---
	const selectedStates = $derived($chartConfig.states);

	const stateSaidiSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			return {
				name: abbr,
				color: CHART_COLORS_CSS[(1 + i) % CHART_COLORS_CSS.length],
				values: data.byStateTrend
					.filter((d: any) => d.stateAbbr === abbr && d[saidiField] != null)
					.map((d: any) => ({ date: d.year, value: d[saidiField] }))
					.sort((a: any, b: any) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const combinedSaidiSeries = $derived([...saidiSeries, ...stateSaidiSeries]);

	// --- Choropleth: SAIDI by state ---
	const mapData = $derived(
		data.byState
			.map((d: any) => ({ state: d.state, fips: d.fips, value: d[saidiField] }))
			.filter((d: { fips: string; value: number | null }) => d.fips && d.value != null)
	);

	// Bar chart data for map/chart toggle
	const mapBarData = $derived(
		[...mapData]
			.sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
			.slice(0, 15)
			.map((d) => ({
				label: d.state,
				value: d.value ?? 0,
			}))
	);

	let reliabilityMapMode = $state<'map' | 'chart'>('map');

	const mapMeta: ChartMeta = $derived({
		title: 'Power Outage Duration by State',
		subtitle: `SAIDI by state (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${data.byState[0]?.year || 2024}`,
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: 'minutes/customer/year',
		lastUpdated: data.lastUpdated,
		description: 'Customer-weighted average outage duration (SAIDI) for each state. Darker colors indicate longer average outages. Southeastern and Gulf Coast states tend to experience more outage minutes due to hurricane and severe weather exposure.',
		caveats: 'State averages are computed from individual utility reports weighted by customers served. States with few reporting utilities may have less reliable averages.',
		relatedCharts: [
			{ title: 'Prices by state', href: '/prices' },
			{ title: 'Renewable share', href: '/generation' },
		],
	});

	// --- Chart 2: SAIDI vs SAIFI scatter ---
	const saidiVsSaifi = $derived(
		data.byState
			.filter((d: any) => d[saidiField] != null && d[saifiField] != null)
			.map((d: any) => ({
				x: d[saidiField],
				y: d[saifiField],
				label: d.stateAbbr || d.state,
				group: d[saidiField] > 500 ? 'High outage states' : 'Other states',
			}))
	);

	const scatterMeta: ChartMeta = $derived({
		title: 'Outage Duration vs Frequency by State',
		subtitle: `SAIDI vs SAIFI (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${data.byState[0]?.year || 2024}`,
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: data.lastUpdated,
		description: 'Each dot is a US state. States with longer average outage duration (SAIDI) tend to also have more frequent interruptions (SAIFI). Data is customer-weighted from utility reports.',
		caveats: 'Southeastern and Gulf Coast states often appear in the upper right due to hurricane exposure. Some states have few reporting utilities, which can skew averages.',
	});

	// --- Market structure map ---
	const marketMap = $derived(new Map<string, string>(
		data.marketStructure.map((d: any) => [d.state, d.market])
	));

	// --- Chart 3: Reliability vs Prices scatter ---
	const latestYear = $derived(data.byState[0]?.year || 2024);

	const reliabilityVsPrices = $derived((() => {
		const priceMap = new Map<string, number>();
		for (const p of data.pricesByState) {
			if (p.year === latestYear && p.sector === 'Residential') {
				priceMap.set(p.state, p.price);
			}
		}
		if (priceMap.size === 0) {
			for (const p of data.pricesByState) {
				if (p.year === latestYear - 1 && p.sector === 'Residential') {
					priceMap.set(p.state, p.price);
				}
			}
		}

		return data.byState
			.filter((d: any) => d[saidiField] != null && priceMap.has(d.state))
			.map((d: any) => ({
				x: d[saidiField],
				y: priceMap.get(d.state)!,
				label: d.stateAbbr || d.state,
				group: marketMap.get(d.state) ?? 'Non-ISO',
			}));
	})());

	const priceScatterMeta: ChartMeta = $derived({
		title: 'Do Unreliable Grids Cost More?',
		subtitle: `SAIDI vs residential electricity price by state (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${latestYear}`,
		source: 'EIA-861 (reliability) + EIA Retail Sales (prices)',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: data.lastUpdated,
		description: 'Compares each state\'s average outage duration (SAIDI) against its residential electricity price. If poor reliability correlated with higher prices, points would trend upward to the right.',
		caveats: 'Electricity prices are driven by many factors (fuel mix, regulation, geography) beyond grid reliability. This chart shows correlation, not causation.',
	});

	// --- Key figures ---
	const kfLatest = $derived(data.national.length > 0 ? data.national[data.national.length - 1] : null);
	const kfLatestSaidi = $derived(kfLatest ? kfLatest.saidi : 0);
	const kfLatestSaidiNoMed = $derived(kfLatest ? kfLatest.saidi_no_med : 0);
	const kfLatestYear = $derived(kfLatest ? kfLatest.year : 0);
	const kfNumStates = $derived(data.byState.length);
	const kfNumUtilities = $derived(kfLatest ? kfLatest.utilities : 0);
</script>

<svelte:head>
	<title>Reliability & Outages — US Energy Data</title>
</svelte:head>

<div>
	<!-- Title + intro -->
	<div class="prose-width">
		<h1 class="text-2xl font-display font-semibold tracking-tight text-text mt-2 mb-4">Reliability & Outages</h1>
		<p class="narrative-text">
			The average American experienced about <span class="inline-stat">~{Math.round(kfLatestSaidi / 60)} hours</span> of power outages in {kfLatestYear}. Excluding major events like hurricanes, the baseline is roughly <span class="inline-stat">{Math.round(kfLatestSaidiNoMed)} minutes</span>. Grid reliability has become a growing concern as extreme weather intensifies and aging infrastructure strains under rising demand.
		</p>
	</div>

	<!-- Section: How long do outages last? -->
	<h2 class="prose-width section-heading">How long do outages last?</h2>
	<p class="prose-width narrative-text">
		The System Average Interruption Duration Index (SAIDI) tracks how many minutes per year the typical customer loses power. The national trend shows a clear upward drift, punctuated by spikes in major-event years.
	</p>

	<div class="chart-breakout mt-6">
		<ChartWrapper meta={lineMeta} data={data.national}>
			{#snippet controls()}
				<Dropdown
					label="Metric"
					options={medOptions}
					value={activeMed}
					onchange={(v) => updateConfig('med', v)}
				/>
				<StateSelect
					selected={selectedStates}
					onchange={(states) => updateConfig('state', states)}
					label=""
					compact
				/>
				{#if hasActiveFilters($chartConfig)}
					<button onclick={resetConfig} class="text-xs text-text-muted hover:text-accent transition-colors">Reset</button>
				{/if}
			{/snippet}
			<LineChart
				series={combinedSaidiSeries}
				xLabel="Year"
				yLabel="Minutes per customer"
				yFormat={format(',.0f')}
				unit="min"
				annotations={activeMed === 'with_med' ? saidiAnnotations : []}
				showTrend={5}
			/>
		</ChartWrapper>
	</div>

	<div class="prose-width mt-6">
		<div class="insight-card">
			<div class="flex items-start gap-4">
				<div class="flex-shrink-0">
					<span class="text-xl font-bold text-accent font-mono">~{Math.round(kfLatestSaidi / 60)}hr</span>
					<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">avg outage ({kfLatestYear})</span>
				</div>
				<p class="text-sm leading-relaxed text-text-secondary">
					The average US customer experienced about {Math.round(kfLatestSaidi / 60)} hours of power outages in {kfLatestYear} — but excluding major events, the baseline is roughly {Math.round(kfLatestSaidiNoMed)} minutes.
				</p>
			</div>
		</div>
	</div>

	<!-- Section: Where is the grid least reliable? -->
	<h2 class="prose-width section-heading">Where is the grid least reliable?</h2>
	<p class="prose-width narrative-text">
		Reliability varies dramatically by state. Southeastern and Gulf Coast states bear the brunt of hurricane exposure, while states with aging distribution networks or extreme winter weather also see elevated outage durations.
	</p>

	<div class="chart-breakout mt-6">
		<ChartWrapper meta={mapMeta} data={mapData}>
			{#snippet controls()}
				<MapChartToggle mode={reliabilityMapMode} onToggle={(m) => { reliabilityMapMode = m; }} />
			{/snippet}
			{#if reliabilityMapMode === 'map'}
				<ChoroplethMap
					data={mapData}
					topology={data.topology}
					colorInterpolator={interpolateYlOrRd}
					valueFormat={format(',.0f')}
					unit="min"
					onStateClick={toggleState}
				/>
			{:else}
				<BarChart
					data={mapBarData}
					horizontal
					yFormat={format(',.0f')}
					unit="min"
					margin={{ top: 20, right: 20, bottom: 60, left: 120 }}
				/>
			{/if}
		</ChartWrapper>
		{#if selectedStates.length > 0}
			<p class="text-xs text-text-muted mt-1">Shows all states — click a state to add it to the trend chart filter</p>
		{/if}
	</div>

	<!-- Section: Do outages and prices correlate? -->
	<h2 class="prose-width section-heading">Do outages and prices correlate?</h2>
	<p class="prose-width narrative-text">
		States that experience longer outages also tend to have more frequent ones — but the link between reliability and electricity prices is weaker than you might expect. Many factors beyond grid performance drive what you pay per kilowatt-hour.
	</p>

	<div class="chart-breakout mt-6">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={scatterMeta} data={data.byState}>
					<Scatter
						data={saidiVsSaifi}
						xLabel="SAIDI (minutes/customer/year)"
						yLabel="SAIFI (interruptions/customer/year)"
						xFormat={format(',.0f')}
						yFormat={format(',.2f')}
						unit=""
					/>
				</ChartWrapper>
			</section>

			<section>
				<ChartWrapper meta={priceScatterMeta} data={reliabilityVsPrices}>
					<Scatter
						data={reliabilityVsPrices}
						xLabel="SAIDI (minutes/customer/year)"
						yLabel="Residential price (cents/kWh)"
						xFormat={format(',.0f')}
						yFormat={format('.1f')}
						unit="c/kWh"
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Cross-link -->
	<p class="prose-width mt-8">
		<a href="/prices" class="text-accent hover:text-accent-light no-underline font-medium">Explore electricity prices in more detail &rarr;</a>
	</p>
</div>
