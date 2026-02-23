<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import DivergingBarChart from '$components/charts/DivergingBarChart.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { format } from 'd3-format';
	import { CHART_COLORS } from '$utils/colors';
	import { formatCompact } from '$utils/formatting';
	import { stateFromAbbr } from '$utils/states';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const consumptionAnnotations = [
		{ date: 2009, label: '09 Recession' },
		{ date: 2020, label: 'COVID-19' },
		{ date: 2022, label: 'IRA' },
	];

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

	// State comparison series
	const selectedStates = $derived($chartConfig.states);

	const stateSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);
			const rows = data.byState.filter((d: any) => d.state === fullName);
			const total = new Map<number, number>();
			for (const row of rows) {
				total.set(row.year, (total.get(row.year) ?? 0) + row.consumption);
			}
			return {
				name: `${abbr} (Total)`,
				color: CHART_COLORS[(filteredSeries.length + i) % CHART_COLORS.length],
				values: [...total.entries()]
					.map(([year, value]) => ({ date: year, value }))
					.sort((a, b) => a.date - b.date),
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
		title: 'Electricity Consumption by Sector',
		subtitle: 'US national total, million kilowatt-hours, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'million kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Total US electricity consumption has grown modestly over the past two decades, with commercial and residential sectors driving most of the increase. Energy efficiency gains have partially offset growth in economic activity and population. Select states to compare against the national totals.',
		caveats: 'Consumption data represents retail sales to end-use customers. It excludes direct-use generation and transmission losses, which can add 5-7% to total electricity demand.',
	};

	// Bar chart: Top 10 states by total consumption (latest year)
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	// Key figures
	const latestTotal = $derived(data.national.filter((d: any) => d.year === latestYear).reduce((sum: number, d: any) => sum + d.consumption, 0));
	const latestTWh = $derived((latestTotal / 1_000_000).toFixed(1));
	const prevYearTotal = $derived(data.national.filter((d: any) => d.year === latestYear - 1).reduce((sum: number, d: any) => sum + d.consumption, 0));
	const yoyGrowth = $derived(prevYearTotal > 0 ? (((latestTotal - prevYearTotal) / prevYearTotal) * 100).toFixed(1) : '0');

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
				color: '#1b9e77',
			}));
	})());

	const topState = $derived(stateRanking.length > 0 ? stateRanking[0] : null);

	// Load Growth chart: year-over-year % change in total consumption
	const loadGrowthSeries: DataSeries[] = $derived((() => {
		const yearTotals = new Map<number, number>();
		for (const d of data.national) {
			yearTotals.set(d.year, (yearTotals.get(d.year) ?? 0) + d.consumption);
		}
		const years = [...yearTotals.entries()].sort((a, b) => a[0] - b[0]);
		const growth = years.slice(1).map(([year, total], i) => {
			const prev = years[i][1];
			return { date: year, value: prev > 0 ? ((total - prev) / prev) * 100 : 0 };
		});
		return [{ name: 'YoY Growth', values: growth }];
	})());

	const timeFilteredGrowth = $derived(
		loadGrowthSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const loadGrowthBars = $derived(
		timeFilteredGrowth[0].values.map((v) => ({
			label: String(v.date),
			value: v.value,
		}))
	);

	const loadGrowthMeta: ChartMeta = {
		title: 'Electricity Demand Growth Rate',
		subtitle: 'Year-over-year change in total US consumption, %',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Annual electricity demand growth has slowed significantly since the 2000s. The 2009 recession caused a sharp drop, followed by tepid growth. Recent years show signs of acceleration driven by data centers, electrification, and economic activity.',
		caveats: 'Growth rates are calculated from total retail sales across all sectors. Negative values indicate years where consumption declined year-over-year.',
	};

	const barMeta: ChartMeta = $derived({
		title: `Top 10 States by Electricity Consumption (${latestYear})`,
		subtitle: 'Total across all sectors, million kWh',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'million kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Texas and California dominate electricity consumption, driven by large populations, industrial activity, and climate-related demand. Texas leads due to its large industrial base, air conditioning load, and oil/gas operations.',
		caveats: 'Rankings reflect total consumption, not per-capita usage. States with smaller populations but high per-capita demand (e.g., Wyoming) do not appear in the top 10 by total volume.',
	});

	// Chart 4: Per-Capita Electricity Consumption by State
	const perCapitaLatestYear = $derived(Math.max(...data.perCapita.map((d: any) => d.year)));

	const perCapitaRanking = $derived((() => {
		return data.perCapita
			.filter((d: any) => d.year === perCapitaLatestYear)
			.sort((a: any, b: any) => b.per_capita_kwh - a.per_capita_kwh)
			.slice(0, 15)
			.map((d: any, i: number) => ({
				label: d.state,
				value: d.per_capita_kwh,
				color: '#1b9e77',
			}));
	})());

	const perCapitaMeta: ChartMeta = $derived({
		title: `Per-Capita Electricity Consumption by State (${perCapitaLatestYear})`,
		subtitle: 'kWh per person per year',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Some states like Wyoming and Louisiana have very high per-capita electricity consumption due to energy-intensive heavy industry (mining, refining, petrochemicals) that inflates usage well beyond household needs. Meanwhile, states like Hawaii and California rank low thanks to mild climates, aggressive efficiency standards, and service-oriented economies.',
		caveats: 'Uses 2023 Census population estimates for all years. Commercial and industrial consumption is included in per-capita calculation.',
	});
</script>

<svelte:head>
	<title>Electricity Demand — US Energy Data</title>
</svelte:head>

<div>
	<!-- Header -->
	<div class="flex items-baseline gap-3 pb-3 border-b border-border">
		<h1 class="text-base font-semibold text-text">Electricity Demand</h1>
		<span class="text-sm text-text-secondary">Where does all the electricity go?</span>
	</div>

	<!-- Sticky control bar -->
	<div class="sticky top-12 z-20 -mx-4 md:-mx-6 lg:-mx-8 bg-surface/95 backdrop-blur-sm border-b border-border px-4 md:px-6 lg:px-8 py-2">
		<div class="flex flex-wrap items-center gap-3">
			<Dropdown
				options={sectorOptions}
				value={activeSector}
				label="Sector"
				onchange={(v) => updateConfig('sector', v)}
			/>
			<StateSelect
				selected={selectedStates}
				onchange={(states) => updateConfig('state', states)}
			/>
			<TimeRangeSlider {startYear} {endYear} />
		</div>
	</div>

	<!-- Key Figures -->
	<div class="flex flex-wrap gap-2 mt-3 mb-1">
		<div class="key-figure">
			<span class="kf-value" style="color: #1b9e77">{latestTWh}T</span>
			<span class="kf-label">kWh consumed ({latestYear})</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #1b9e77">{yoyGrowth}%</span>
			<span class="kf-label">year-over-year growth</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #1b9e77">{topState ? topState.label.slice(0, 5) : '—'}</span>
			<span class="kf-label">top consumer</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #1b9e77">{latestYear}</span>
			<span class="kf-label">latest year</span>
		</div>
	</div>

	<!-- Chart grid -->
	<div class="grid gap-3 lg:grid-cols-2 mt-3">
		<!-- Consumption trends (full-width hero) -->
		<section class="lg:col-span-2">
			<ChartWrapper meta={lineMeta} hero data={timeFilteredSeries.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, consumption: v.value })))}>
				<LineChart
					series={timeFilteredSeries}
					xLabel="Year"
					yLabel="million kWh"
					yFormat={formatCompact}
					unit="million kWh"
					margin={{ top: 20, right: 20, bottom: 40, left: 70 }}
					annotations={consumptionAnnotations}
				/>
			</ChartWrapper>
		</section>

		<!-- Growth bar (full-width) -->
		<section class="lg:col-span-2">
			<ChartWrapper meta={loadGrowthMeta} data={loadGrowthBars.map((d) => ({ year: d.label, growth_pct: d.value }))}>
				<DivergingBarChart
					data={loadGrowthBars}
					yLabel="% change"
					yFormat={format('+.1f')}
					unit="%"
				/>
			</ChartWrapper>
		</section>

		<!-- Insight (full-width) -->
		<div class="lg:col-span-2 insight-card">
			<div class="flex items-start gap-4">
				<div class="flex-shrink-0">
					<span class="text-xl font-bold text-accent" style="font-family: var(--font-mono)">&lt;1%</span>
					<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">annual growth</span>
				</div>
				<p class="text-sm leading-relaxed text-text-secondary">
					US electricity demand grew less than 1% per year from 2010 to 2020 — but data centers and electrification are accelerating growth again.
				</p>
			</div>
		</div>

		<!-- Top states + Per-capita (side-by-side) -->
		<section>
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

		<section>
			<ChartWrapper meta={perCapitaMeta} data={perCapitaRanking.map((d: any) => ({ state: d.label, per_capita_kwh: d.value }))}>
				<BarChart
					data={perCapitaRanking}
					horizontal
					yLabel="kWh"
					yFormat={formatCompact}
					unit="kWh"
					margin={{ top: 20, right: 20, bottom: 60, left: 120 }}
				/>
			</ChartWrapper>
		</section>
	</div>

	<!-- Cross-links -->
	<p class="mt-3 text-sm">
		<a href="/prices" class="text-accent/80 hover:text-accent transition-colors no-underline">How much does this electricity cost? Explore prices &rarr;</a>
	</p>
</div>
