<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import { CHART_COLORS } from '$utils/colors';
	import { formatCompact } from '$utils/formatting';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const FUEL_COLORS: Record<string, string> = {
		'Coal': '#4a4a4a',
		'Natural Gas': '#e86c3a',
		'Crude Oil': '#a6611a',
	};

	const fuelOptions = [
		{ value: 'all', label: 'All Fuels' },
		{ value: 'Coal', label: 'Coal' },
		{ value: 'Natural Gas', label: 'Natural Gas' },
		{ value: 'Crude Oil', label: 'Crude Oil' },
	];

	let selectedFuel = $state('all');

	// Line chart: National production trends (raw values)
	const allFuelSeries: DataSeries[] = $derived((() => {
		const fuels = [...new Set(data.national.map((d: any) => d.fuel))] as string[];
		return fuels.map((fuel) => ({
			name: fuel,
			color: FUEL_COLORS[fuel] ?? '#999',
			values: data.national
				.filter((d: any) => d.fuel === fuel)
				.map((d: any) => ({ date: d.year, value: d.production }))
				.sort((a: any, b: any) => a.date - b.date),
		}));
	})());

	// Indexed series for "All Fuels" view: base year = 100
	const indexedFuelSeries: DataSeries[] = $derived((() => {
		return allFuelSeries.map((series) => {
			const baseValue = series.values.length > 0 ? series.values[0].value : 1;
			return {
				...series,
				values: series.values.map((v) => ({
					date: v.date,
					value: baseValue !== 0 ? (v.value / baseValue) * 100 : 0,
				})),
			};
		});
	})());

	const filteredFuelSeries = $derived(
		selectedFuel === 'all'
			? indexedFuelSeries
			: allFuelSeries.filter((s) => s.name === selectedFuel)
	);

	const lineYLabel = $derived(
		selectedFuel === 'all'
			? 'Index (base year = 100)'
			: selectedFuel === 'Coal' ? 'short tons' : selectedFuel === 'Natural Gas' ? 'million cu ft' : 'thousand barrels'
	);

	const lineMeta: ChartMeta = {
		title: 'US Fossil Fuel Production Over Time',
		subtitle: 'National annual totals',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/',
		unit: 'varies by fuel',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'US fossil fuel production has evolved significantly, with natural gas and crude oil production reaching record levels while coal has declined.',
		caveats: 'Units differ by fuel type: coal (short tons), natural gas (million cubic feet), crude oil (thousand barrels). Trends shown on separate scales when viewing individual fuels.',
	};

	// Bar chart: Top 10 producing states for selected fuel
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	const barFuel = $derived(selectedFuel === 'all' ? 'Coal' : selectedFuel);

	const stateRanking = $derived((() => {
		const stateData = data.byState.filter(
			(d: any) => d.year === latestYear && d.fuel === barFuel
		);
		return stateData
			.sort((a: any, b: any) => b.production - a.production)
			.slice(0, 10)
			.map((d: any, i: number) => ({
				label: d.state,
				value: d.production,
				color: CHART_COLORS[i % CHART_COLORS.length],
			}));
	})());

	const barUnit = $derived(
		barFuel === 'Coal' ? 'short tons' : barFuel === 'Natural Gas' ? 'million cu ft' : 'thousand barrels'
	);

	const barMeta: ChartMeta = $derived({
		title: `Top 10 ${barFuel} Producing States (${latestYear})`,
		subtitle: barUnit,
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/',
		unit: barUnit,
		lastUpdated: new Date().toISOString().split('T')[0],
	});
</script>

<svelte:head>
	<title>Fossil Fuels — US Energy Data</title>
</svelte:head>

<div class="space-y-16">
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Fossil Fuels</h1>
		<p class="mt-3 max-w-3xl text-base leading-relaxed text-text-secondary">
			Coal, natural gas, and crude oil production across the United States. The US is one of the world's largest fossil fuel producers, with production patterns that vary significantly by region.
		</p>
	</header>

	<!-- Chart 1: Production trends -->
	<section>
		<div class="mb-5 flex flex-wrap items-end gap-4">
			<Dropdown
				options={fuelOptions}
				value={selectedFuel}
				label="Fuel Type"
				onchange={(v) => selectedFuel = v}
			/>
		</div>

		<ChartWrapper meta={lineMeta} data={filteredFuelSeries.flatMap((s) => s.values.map((v) => ({ fuel: s.name, year: v.date, production: v.value })))}>
			<LineChart
				series={filteredFuelSeries}
				xLabel="Year"
				yLabel={lineYLabel}
				yFormat={selectedFuel === 'all' ? format(',.0f') : formatCompact}
				unit={selectedFuel === 'all' ? '' : barUnit}
				margin={{ top: 20, right: 20, bottom: 40, left: 70 }}
			/>
		</ChartWrapper>
		{#if selectedFuel === 'all'}
			<p class="mt-3 text-sm text-text-muted">
				Values indexed to first available year (= 100) to enable comparison across fuels with different units.
			</p>
		{/if}
	</section>

	<!-- Chart 2: Top producing states -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl">
		<ChartWrapper meta={barMeta} data={stateRanking.map((d) => ({ state: d.label, production: d.value }))}>
			<BarChart
				data={stateRanking}
				horizontal
				yLabel={barUnit}
				yFormat={formatCompact}
				unit={barUnit}
				margin={{ top: 20, right: 20, bottom: 60, left: 120 }}
			/>
		</ChartWrapper>
	</section>
</div>
