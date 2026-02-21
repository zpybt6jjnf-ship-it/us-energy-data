<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { format } from 'd3-format';
	import { CHART_COLORS } from '$utils/colors';
	import { formatCompact } from '$utils/formatting';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const sectorOptions = [
		{ value: 'all', label: 'All Sectors' },
		{ value: 'residential', label: 'Residential' },
		{ value: 'commercial', label: 'Commercial' },
		{ value: 'industrial', label: 'Industrial' },
	];

	const activeSector = $derived(
		$chartConfig.sector === 'residential' || $chartConfig.sector === 'commercial' || $chartConfig.sector === 'industrial'
			? $chartConfig.sector
			: 'all'
	);

	// Line chart: National consumption trends by sector
	const allSeries: DataSeries[] = $derived((() => {
		const sectors = [...new Set(data.national.map((d: any) => d.sector))] as string[];
		return sectors.map((sector) => ({
			name: sector,
			values: data.national
				.filter((d: any) => d.sector === sector)
				.map((d: any) => ({ date: d.year, value: d.consumption }))
				.sort((a: any, b: any) => a.date - b.date),
		}));
	})());

	const filteredSeries = $derived(
		activeSector === 'all'
			? allSeries
			: allSeries.filter((s) => s.name.toLowerCase() === activeSector)
	);

	const lineMeta: ChartMeta = {
		title: 'Electricity Consumption by Sector',
		subtitle: 'US national total, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'million kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Total US electricity consumption has grown modestly over the past two decades, with commercial and residential sectors driving most of the increase.',
	};

	// Bar chart: Top 10 states by total consumption (latest year)
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	const stateRanking = $derived((() => {
		const latestState = data.byState.filter((d: any) => d.year === latestYear);
		const totals = new Map<string, number>();
		for (const row of latestState) {
			totals.set(row.state, (totals.get(row.state) ?? 0) + row.consumption);
		}
		return [...totals.entries()]
			.sort((a, b) => b[1] - a[1])
			.slice(0, 10)
			.map(([state, consumption], i) => ({
				label: state,
				value: consumption,
				color: CHART_COLORS[i % CHART_COLORS.length],
			}));
	})());

	const barMeta: ChartMeta = $derived({
		title: `Top 10 States by Electricity Consumption (${latestYear})`,
		subtitle: 'Total across all sectors',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'million kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Texas and California dominate electricity consumption, driven by large populations, industrial activity, and climate-related demand.',
	});
</script>

<svelte:head>
	<title>Electricity Demand — US Energy Data</title>
</svelte:head>

<div class="space-y-16">
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Electricity Demand</h1>
		<p class="mt-3 max-w-3xl text-base leading-relaxed text-text-secondary">
			How much electricity does the US consume, and where is demand highest? Consumption patterns reveal the structure of the economy and the impact of efficiency gains.
		</p>
	</header>

	<!-- Chart 1: Consumption trends -->
	<section>
		<div class="mb-5 flex flex-wrap items-end gap-4">
			<Dropdown
				options={sectorOptions}
				value={activeSector}
				label="Sector"
				onchange={(v) => updateConfig('sector', v)}
			/>
		</div>

		<ChartWrapper meta={lineMeta} data={filteredSeries.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, consumption: v.value })))}>
			<LineChart
				series={filteredSeries}
				xLabel="Year"
				yLabel="million kWh"
				yFormat={formatCompact}
				unit="million kWh"
				margin={{ top: 20, right: 20, bottom: 40, left: 70 }}
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 2: State ranking -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl">
		<ChartWrapper meta={barMeta} data={stateRanking.map((d) => ({ state: d.label, consumption: d.value }))}>
			<BarChart
				data={stateRanking}
				horizontal
				yLabel="million kWh"
				yFormat={formatCompact}
				unit="million kWh"
				margin={{ top: 20, right: 20, bottom: 60, left: 120 }}
			/>
		</ChartWrapper>
	</section>
</div>
