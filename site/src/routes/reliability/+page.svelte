<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	// Line chart: National SAIDI trend
	const saidiSeries: DataSeries[] = $derived([
		{
			name: 'SAIDI (avg. interruption minutes)',
			values: data.national.map((d: any) => ({
				date: d.year,
				value: d.saidi,
			})),
		},
	]);

	const lineMeta: ChartMeta = {
		title: 'Average Power Outage Duration Over Time',
		subtitle: 'System Average Interruption Duration Index (SAIDI), US national average',
		source: 'IEEE 1366 / EIA-861 estimates',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: 'minutes/customer/year',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'SAIDI measures the average total duration of power interruptions experienced by each customer per year. Spikes often correspond to major weather events such as hurricanes or winter storms.',
		caveats: 'Sample data. Real integration with FERC Form 714 and EIA-861 planned for Phase 2.',
	};

	// Scatter: SAIDI vs electricity price by state
	const scatterData = $derived(
		data.byState.map((d: any) => ({
			x: d.saidi,
			y: 0, // placeholder — will be enriched when we add price data
			label: d.state,
			group: d.saidi > 300 ? 'High outage' : d.saidi > 200 ? 'Medium' : 'Low outage',
		}))
	);

	// For the scatter, we'll show SAIDI vs SAIFI instead (both available)
	const saidiVsSaifi = $derived(
		data.byState.map((d: any) => ({
			x: d.saidi,
			y: d.saifi ?? 0,
			label: d.state,
			group: d.saidi > 350 ? 'High outage states' : 'Other states',
		}))
	);

	const scatterMeta: ChartMeta = {
		title: 'Outage Duration vs Frequency by State',
		subtitle: 'SAIDI (minutes) vs SAIFI (number of interruptions)',
		source: 'IEEE 1366 / EIA-861 estimates',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'States with longer average outage duration (SAIDI) also tend to have more frequent interruptions (SAIFI). Southeastern and northeastern states face higher reliability challenges.',
		caveats: 'Sample data. Real integration with FERC Form 714 and EIA-861 planned for Phase 2.',
	};
</script>

<svelte:head>
	<title>Reliability & Outages — US Energy Data</title>
</svelte:head>

<div class="space-y-16">
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Reliability & Outages</h1>
		<p class="mt-3 max-w-3xl text-base leading-relaxed text-text-secondary">
			How reliable is the US power grid? Outage trends, state comparisons, and the relationship between outage frequency and duration.
		</p>
	</header>

	<!-- Sample data banner -->
	<div class="rounded-lg border border-amber-200 bg-amber-50 px-5 py-4">
		<p class="text-sm font-medium text-amber-800">
			This page uses representative sample data based on publicly reported averages. Real integration with FERC Form 714 and EIA-861 reliability metrics is planned for Phase 2.
		</p>
	</div>

	<!-- Chart 1: National SAIDI trend -->
	<section>
		<ChartWrapper meta={lineMeta} data={data.national}>
			<LineChart
				series={saidiSeries}
				xLabel="Year"
				yLabel="Minutes per customer"
				yFormat={format(',.0f')}
				unit="min"
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 2: SAIDI vs SAIFI scatter -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl">
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
</div>
