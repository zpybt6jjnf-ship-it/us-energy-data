<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { chartConfig, updateConfig, hasActiveFilters, resetConfig } from '$stores/chartConfig';
	import { CHART_COLORS, FUEL_COLORS, FUEL_GEN_COLORS, TRADE_COLORS, STATE_BAR_COLOR } from '$utils/colors';
	import { formatCompact } from '$utils/formatting';
	import { stateFromAbbr } from '$utils/states';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const productionAnnotations = [
		{ date: 2008, label: 'Shale revolution' },
		{ date: 2020, label: 'COVID-19' },
		{ date: 2022, label: 'IRA' },
	];

	const fuelOptions = [
		{ value: 'all', label: 'All Fuels' },
		{ value: 'Coal', label: 'Coal' },
		{ value: 'Natural Gas', label: 'Natural Gas' },
		{ value: 'Crude Oil', label: 'Crude Oil' },
	];

	const selectedFuel = $derived($chartConfig.fuel);

	const startYear = $derived($chartConfig.startYear);
	const endYear = $derived($chartConfig.endYear);

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

	const selectedStates = $derived($chartConfig.states);

	const stateSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);

			if (selectedFuel === 'all') {
				const fuels = [...new Set(data.byState.filter((d: any) => d.state === fullName).map((d: any) => d.fuel))] as string[];
				const fuelIndices = fuels.map((fuel) => {
					const rows = data.byState
						.filter((d: any) => d.state === fullName && d.fuel === fuel)
						.sort((a: any, b: any) => a.year - b.year);
					if (rows.length === 0) return [];
					const baseValue = rows[0].production;
					return rows.map((r: any) => ({
						date: r.year,
						value: baseValue !== 0 ? (r.production / baseValue) * 100 : 0,
					}));
				}).filter((v) => v.length > 0);

				const yearMap = new Map<number, { sum: number; count: number }>();
				for (const series of fuelIndices) {
					for (const pt of series) {
						const entry = yearMap.get(pt.date) ?? { sum: 0, count: 0 };
						entry.sum += pt.value;
						entry.count += 1;
						yearMap.set(pt.date, entry);
					}
				}

				return {
					name: `${abbr} (Indexed)`,
					color: CHART_COLORS[(filteredFuelSeries.length + i) % CHART_COLORS.length],
					values: [...yearMap.entries()]
						.map(([date, { sum, count }]) => ({ date, value: sum / count }))
						.sort((a, b) => a.date - b.date),
				};
			} else {
				const rows = data.byState
					.filter((d: any) => d.state === fullName && d.fuel === selectedFuel)
					.sort((a: any, b: any) => a.year - b.year);
				return {
					name: `${abbr} (${selectedFuel})`,
					color: CHART_COLORS[(filteredFuelSeries.length + i) % CHART_COLORS.length],
					values: rows.map((r: any) => ({ date: r.year, value: r.production })),
				};
			}
		}).filter((s) => s.values.length > 0)
	);

	const combinedSeries = $derived([...filteredFuelSeries, ...stateSeries]);

	const timeFilteredCombined = $derived(
		combinedSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
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
		lastUpdated: data.lastUpdated,
		description: 'US fossil fuel production has evolved significantly. The shale revolution (post-2008) drove natural gas and crude oil to record levels, while coal production has declined steadily as power plants switch to cheaper gas and renewables.',
		caveats: 'Units differ by fuel type: coal (short tons), natural gas (million cubic feet), crude oil (thousand barrels). When "All Fuels" is selected, values are indexed to the first available year (= 100) to enable fair cross-fuel comparison despite different units.',
	};

	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	const barFuel = $derived(selectedFuel === 'all' ? 'Coal' : selectedFuel);

	const stateRanking = $derived((() => {
		const stateData = data.byState.filter(
			(d: any) => d.year === latestYear && d.fuel === barFuel
		);
		return stateData
			.sort((a: any, b: any) => b.production - a.production)
			.slice(0, 10)
			.map((d: any) => ({
				label: d.state,
				value: d.production,
				color: STATE_BAR_COLOR,
			}));
	})());

	const barUnit = $derived(
		barFuel === 'Coal' ? 'short tons' : barFuel === 'Natural Gas' ? 'million cu ft' : 'thousand barrels'
	);

	// Fossil fuel generation over time
	const fuelGenSeries: DataSeries[] = $derived((() => {
		const fossilSources = ['Coal', 'Natural Gas', 'Petroleum'];
		return fossilSources.map((source) => ({
			name: source,
			color: FUEL_GEN_COLORS[source] ?? '#999',
			values: data.generation
				.filter((d: any) => d.source === source)
				.map((d: any) => ({ date: d.year, value: d.generation }))
				.sort((a: any, b: any) => a.date - b.date),
		})).filter((s) => s.values.length > 0);
	})());

	const timeFilteredFuelGen = $derived(
		fuelGenSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const fuelGenMeta: ChartMeta = {
		title: 'Electricity Generation from Fossil Fuels',
		subtitle: 'Thousand megawatt-hours by fuel type, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'thousand MWh',
		lastUpdated: data.lastUpdated,
		description: 'How much electricity does each fossil fuel generate? Coal-fired generation has declined sharply since its peak around 2007, while natural gas generation has surged. Petroleum (oil) plays a minimal and declining role in US electricity generation.',
		caveats: 'Generation data represents net generation at utility-scale power plants. Combined heat and power (CHP) facilities are included. Some natural gas generation comes from plants that can also burn oil as backup fuel.',
	};

	// US Petroleum Trade
	const tradeSeries: DataSeries[] = $derived((() => {
		const petTrade = data.trade
			.filter((d: any) => d.fuel === 'Petroleum' && d.year >= 2000)
			.sort((a: any, b: any) => a.year - b.year);

		return [
			{ name: 'Imports', color: TRADE_COLORS['Imports'], values: petTrade.map((d: any) => ({ date: d.year, value: d.imports })) },
			{ name: 'Exports', color: TRADE_COLORS['Exports'], values: petTrade.map((d: any) => ({ date: d.year, value: d.exports })) },
			{ name: 'Net Imports', color: TRADE_COLORS['Net Imports'], values: petTrade.map((d: any) => ({ date: d.year, value: d.net_imports })) },
		];
	})());

	const timeFilteredTrade = $derived(
		tradeSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const tradeAnnotations = [
		{ date: 2008, label: 'Shale revolution' },
		{ date: 2020, label: 'COVID-19' },
		{ date: 2022, label: 'IRA' },
	];

	const tradeMeta: ChartMeta = {
		title: 'US Petroleum Trade',
		subtitle: 'Thousand barrels per day',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/petroleum/move/',
		unit: 'thousand barrels/day',
		lastUpdated: data.lastUpdated,
		description: 'The US was a major net petroleum importer for decades, but the shale revolution and increased domestic production have dramatically reduced net imports. Since roughly 2020 the US has been close to energy self-sufficiency in petroleum, with exports rising sharply even as imports have moderated.',
		caveats: 'Includes crude oil and finished petroleum products. Net imports = imports minus exports. A negative net imports value indicates the US is a net exporter. Data from EIA petroleum movement series.',
	};

	// US Natural Gas Trade
	const gasTradeSeries: DataSeries[] = $derived((() => {
		const gasTrade = data.trade
			.filter((d: any) => d.fuel === 'Natural Gas' && d.year >= 2000)
			.sort((a: any, b: any) => a.year - b.year);
		return [
			{ name: 'Imports', color: TRADE_COLORS['Imports'], values: gasTrade.map((d: any) => ({ date: d.year, value: d.imports })) },
			{ name: 'Exports', color: TRADE_COLORS['Exports'], values: gasTrade.map((d: any) => ({ date: d.year, value: d.exports })) },
			{ name: 'Net Imports', color: TRADE_COLORS['Net Imports'], values: gasTrade.map((d: any) => ({ date: d.year, value: d.net_imports })) },
		];
	})());

	const timeFilteredGasTrade = $derived(
		gasTradeSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const gasTradeMeta: ChartMeta = {
		title: 'US Natural Gas Trade',
		subtitle: 'Million cubic feet',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/naturalgas/data.php',
		unit: 'million cu ft',
		lastUpdated: data.lastUpdated,
		description: 'The US was a net natural gas importer for decades, relying on pipeline imports from Canada. The shale revolution unlocked vast domestic gas reserves, and the buildout of LNG export terminals transformed the US into a net gas exporter by around 2017 — a historic reversal.',
		caveats: 'Includes pipeline trade (primarily with Canada and Mexico) and LNG shipments. Net imports = imports minus exports. A negative net imports value indicates the US is a net exporter.',
	};

	// Key figures
	const kfTopProducer = $derived(stateRanking.length > 0 ? stateRanking[0].label : '—');
	const kfNumFuels = 3;

	const barMeta: ChartMeta = $derived({
		title: `Top 10 ${barFuel} Producing States (${latestYear})`,
		subtitle: barUnit,
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/',
		unit: barUnit,
		lastUpdated: data.lastUpdated,
		description: `Fossil fuel production is highly concentrated geographically. ${barFuel === 'Coal' ? 'Wyoming alone produces roughly 40% of US coal, primarily from Powder River Basin surface mines.' : barFuel === 'Natural Gas' ? 'Texas and Pennsylvania lead natural gas production, driven by the Permian Basin and Marcellus Shale respectively.' : 'Texas dominates crude oil production, followed by New Mexico (Permian Basin) and North Dakota (Bakken formation).'}`,
		caveats: 'State-level production data may include estimates for months not yet reported. Rankings can shift year-to-year based on market conditions and weather.',
	});
</script>

<svelte:head>
	<title>Fossil Fuels — US Energy Data</title>
</svelte:head>

<div>
	<!-- Title + intro -->
	<div class="prose-width">
		<h1 class="text-2xl font-display tracking-tight text-text">Fossil Fuels</h1>
		<p class="narrative-text mt-4">
			The US is the world's largest producer of oil and natural gas. The shale revolution, which began around 2008, transformed the energy landscape — natural gas production has roughly <span class="inline-stat">doubled</span> while coal output has fallen by nearly half. In {latestYear}, {kfTopProducer} led {barFuel.toLowerCase()} production.
		</p>
	</div>

	<!-- Controls -->
	<div class="chart-breakout border-y border-border py-3 my-6">
		<div class="flex flex-wrap items-center gap-3">
			<span class="text-sm text-text-muted font-medium">Filter:</span>
			<Dropdown
				options={fuelOptions}
				value={selectedFuel}
				label="Fuel Type"
				onchange={(v) => updateConfig('fuel', v)}
			/>
			<StateSelect
				selected={selectedStates}
				onchange={(states) => updateConfig('state', states)}
			/>
			<TimeRangeSlider {startYear} {endYear} />
			{#if hasActiveFilters($chartConfig)}
				<button onclick={resetConfig} class="text-xs text-text-muted hover:text-accent transition-colors ml-auto">Reset</button>
			{/if}
		</div>
	</div>

	<!-- Section: Production trends -->
	<div class="prose-width">
		<h2 class="section-heading">How has fossil fuel production changed?</h2>
		<p class="narrative-text">
			Since the shale revolution began, US fossil fuel production has diverged dramatically. Natural gas and crude oil surged to record highs while coal entered a steep decline, displaced by cheaper gas and growing renewables. The COVID-19 pandemic caused a brief dip in 2020, but production quickly rebounded.
		</p>
	</div>

	<div class="chart-breakout">
		<ChartWrapper meta={lineMeta} data={timeFilteredCombined.flatMap((s) => s.values.map((v) => ({ fuel: s.name, year: v.date, production: v.value })))}>
			<LineChart
				series={timeFilteredCombined}
				xLabel="Year"
				yLabel={lineYLabel}
				yFormat={selectedFuel === 'all' ? format(',.0f') : formatCompact}
				unit={selectedFuel === 'all' ? '' : barUnit}
				margin={{ top: 20, right: 20, bottom: 40, left: 70 }}
				annotations={productionAnnotations}
			/>
		</ChartWrapper>
		{#if selectedFuel === 'all'}
			<p class="mt-1 text-xs text-text-muted">
				Values indexed to first available year (= 100) to enable comparison across fuels with different units.
			</p>
		{/if}
	</div>

	<!-- Section: Geographic concentration -->
	<div class="prose-width">
		<h2 class="section-heading">Where is production concentrated?</h2>
		<p class="narrative-text">
			Fossil fuel production is highly concentrated in a handful of states. {barFuel === 'Coal' ? 'Wyoming alone produces roughly 40% of US coal from the Powder River Basin.' : barFuel === 'Natural Gas' ? 'Texas and Pennsylvania dominate natural gas output, driven by the Permian Basin and Marcellus Shale.' : 'Texas leads crude oil production by a wide margin, followed by New Mexico and North Dakota.'} Meanwhile, the shift from coal to gas for electricity generation has reshaped the power sector.
		</p>
	</div>

	<div class="chart-breakout">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={barMeta} data={stateRanking.map((d: any) => ({ state: d.label, production: d.value }))}>
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

			<section>
				<ChartWrapper meta={fuelGenMeta} data={timeFilteredFuelGen.flatMap((s) => s.values.map((v) => ({ fuel: s.name, year: v.date, generation: v.value })))}>
					<LineChart
						series={timeFilteredFuelGen}
						xLabel="Year"
						yLabel="thousand MWh"
						yFormat={formatCompact}
						unit="thousand MWh"
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Insight card -->
	<div class="prose-width">
		<div class="insight-card">
			<div class="flex items-start gap-4">
				<div class="flex-shrink-0">
					<span class="text-xl font-bold text-accent font-mono">2x</span>
					<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">gas growth</span>
				</div>
				<p class="text-sm leading-relaxed text-text-secondary">
					US natural gas production has roughly doubled since 2008, while coal output has declined by nearly half — a seismic shift driven by the shale revolution.
				</p>
			</div>
		</div>
	</div>

	<!-- Section: Energy independence -->
	<div class="prose-width">
		<h2 class="section-heading">Has the US achieved energy independence?</h2>
		<p class="narrative-text">
			For decades the US was a major net importer of both petroleum and natural gas. The shale revolution changed that. Surging domestic production slashed petroleum net imports and turned the US into a net natural gas exporter by around 2017. By 2020, the US was effectively energy self-sufficient in petroleum for the first time in half a century.
		</p>
	</div>

	<div class="chart-breakout">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={tradeMeta} data={timeFilteredTrade.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, value: v.value })))}>
					<LineChart
						series={timeFilteredTrade}
						xLabel="Year"
						yLabel="thousand barrels/day"
						yFormat={formatCompact}
						unit="thousand barrels/day"
						annotations={tradeAnnotations}
					/>
				</ChartWrapper>
			</section>

			<section>
				<ChartWrapper meta={gasTradeMeta} data={timeFilteredGasTrade.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, value: v.value })))}>
					<LineChart
						series={timeFilteredGasTrade}
						xLabel="Year"
						yLabel="million cu ft"
						yFormat={formatCompact}
						unit="million cu ft"
						annotations={tradeAnnotations}
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Cross-link -->
	<p class="prose-width mt-8">
		<a href="/generation" class="text-accent hover:text-accent-light no-underline font-medium">See how these fuels translate into electricity generation &rarr;</a>
	</p>
</div>
