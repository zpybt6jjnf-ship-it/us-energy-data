<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { stateFips } from '$utils/states';
	import { interpolateRdYlGn } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

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

	const lineMeta: ChartMeta = {
		title: 'Retail Electricity Prices by Sector',
		subtitle: 'US national average, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'cents/kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Average retail electricity prices vary significantly across sectors. Residential customers typically pay the highest rates due to distribution costs, while industrial users benefit from bulk pricing.',
	};

	// State-level map data: latest year residential prices
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	const mapData = $derived(
		data.byState
			.filter((d: any) => d.year === latestYear && d.sector === 'Residential')
			.map((d: any) => ({
				state: d.state,
				fips: stateFips(d.state),
				value: d.price,
			}))
			.filter((d: any) => d.fips)
	);

	const mapMeta: ChartMeta = $derived({
		title: `Residential Electricity Prices by State (${latestYear})`,
		subtitle: 'Cents per kilowatt-hour',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'cents/kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Electricity prices vary widely across states, driven by differences in fuel mix, regulatory environment, and infrastructure costs.',
	});

	// Reverse interpolator so green = cheap, red = expensive
	function reverseRdYlGn(t: number): string {
		return interpolateRdYlGn(1 - t);
	}
</script>

<svelte:head>
	<title>Prices & Bills — US Energy Data</title>
</svelte:head>

<div class="space-y-16">
	<!-- Header -->
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Prices & Bills</h1>
		<p class="mt-3 max-w-3xl text-base leading-relaxed text-text-secondary">
			How much does electricity cost across the United States? Retail electricity prices differ substantially by sector and geography, shaped by local fuel mix, regulation, and infrastructure.
		</p>
	</header>

	<!-- Chart 1: National price trends -->
	<section>
		<div class="mb-5 flex flex-wrap items-end gap-4">
			<Dropdown
				options={sectorOptions}
				value={activeSector}
				label="Sector"
				onchange={(v) => updateConfig('sector', v)}
			/>
		</div>

		<ChartWrapper meta={lineMeta} data={filteredSeries.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, price: v.value })))}>
			<LineChart
				series={filteredSeries}
				xLabel="Year"
				yLabel="cents/kWh"
				yFormat={format(',.1f')}
				unit="cents/kWh"
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 2: State map -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl">
		<ChartWrapper meta={mapMeta} data={mapData.map((d: any) => ({ state: d.state, price: d.value }))}>
			<ChoroplethMap
				data={mapData}
				topology={data.topology}
				colorInterpolator={reverseRdYlGn}
				valueFormat={format(',.1f')}
				unit="cents/kWh"
			/>
		</ChartWrapper>
	</section>
</div>
