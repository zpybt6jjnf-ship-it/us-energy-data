<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import { ENERGY_SOURCE_COLORS } from '$utils/colors';
	import { stateFips } from '$utils/states';
	import { formatCompact } from '$utils/formatting';
	import { interpolateGreens } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	// Bar chart: Generation by source (latest year)
	const sourceBreakdown = $derived(
		data.national
			.filter((d: any) => d.year === latestYear)
			.sort((a: any, b: any) => b.generation - a.generation)
			.map((d: any) => ({
				label: d.source,
				value: d.generation,
				color: ENERGY_SOURCE_COLORS[d.source.toLowerCase()] ?? '#999',
			}))
	);

	const barMeta: ChartMeta = $derived({
		title: `Electricity Generation by Source (${latestYear})`,
		subtitle: 'Thousand megawatt-hours',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'thousand MWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Natural gas has overtaken coal as the dominant source of US electricity, while wind and solar have grown rapidly from a small base.',
	});

	// Line chart: Key source trends over time
	const trendSources = ['Coal', 'Natural Gas', 'Nuclear', 'Wind', 'Solar'];
	const trendSeries: DataSeries[] = $derived(
		trendSources.map((source) => ({
			name: source,
			color: ENERGY_SOURCE_COLORS[source.toLowerCase()] ?? '#999',
			values: data.national
				.filter((d: any) => d.source === source)
				.map((d: any) => ({ date: d.year, value: d.share }))
				.sort((a: any, b: any) => a.date - b.date),
		})).filter((s) => s.values.length > 0)
	);

	const lineMeta: ChartMeta = {
		title: 'Generation Share by Source Over Time',
		subtitle: 'Percentage of total US generation',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'The share of coal in US electricity generation has fallen dramatically, replaced largely by natural gas and renewables.',
	};

	// Choropleth: Renewable share by state
	const mapData = $derived(
		data.renewableShare
			.map((d: any) => ({
				state: d.state,
				fips: stateFips(d.state),
				value: d.renewable_share,
			}))
			.filter((d: any) => d.fips)
	);

	const mapMeta: ChartMeta = $derived({
		title: `Renewable Energy Share by State (${latestYear})`,
		subtitle: 'Wind + Solar + Hydro as % of total generation',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Renewable energy penetration varies dramatically by state, with western and plains states leading due to abundant wind, hydro, and solar resources.',
	});
</script>

<svelte:head>
	<title>Generation & Resources — US Energy Data</title>
</svelte:head>

<div class="space-y-16">
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Generation & Resources</h1>
		<p class="mt-3 max-w-3xl text-base leading-relaxed text-text-secondary">
			Where does US electricity come from? The generation mix is shifting rapidly as renewables grow and coal declines, reshaping the energy landscape.
		</p>
	</header>

	<!-- Chart 1: Generation by source (bar) -->
	<section>
		<ChartWrapper meta={barMeta} data={sourceBreakdown.map((d: any) => ({ source: d.label, generation: d.value }))}>
			<BarChart
				data={sourceBreakdown}
				horizontal
				yLabel="thousand MWh"
				yFormat={formatCompact}
				unit="thousand MWh"
				margin={{ top: 20, right: 20, bottom: 60, left: 110 }}
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 2: Source share trends (line) -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl">
		<ChartWrapper meta={lineMeta} data={trendSeries.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, share: v.value })))}>
			<LineChart
				series={trendSeries}
				xLabel="Year"
				yLabel="% of total"
				yFormat={format(',.1f')}
				unit="%"
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 3: Renewable share map -->
	<section>
		<ChartWrapper meta={mapMeta} data={mapData.map((d: any) => ({ state: d.state, renewable_share: d.value }))}>
			<ChoroplethMap
				data={mapData}
				topology={data.topology}
				colorInterpolator={interpolateGreens}
				valueFormat={format(',.1f')}
				unit="%"
			/>
		</ChartWrapper>
	</section>
</div>
