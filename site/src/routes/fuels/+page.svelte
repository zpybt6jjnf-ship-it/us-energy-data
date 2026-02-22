<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { CHART_COLORS } from '$utils/colors';
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

	const startYear = $derived($chartConfig.startYear);
	const endYear = $derived($chartConfig.endYear);

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

	// State comparison series
	const selectedStates = $derived($chartConfig.states);

	const stateSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);

			if (selectedFuel === 'all') {
				// Index each fuel for this state, then average across fuels
				// Or more useful: sum production per year across fuels, then index
				// Since units differ, index each fuel separately then average the indices
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

				// Average the indexed values across fuels for each year
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
				// Single fuel: use raw production values
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
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'US fossil fuel production has evolved significantly. The shale revolution (post-2008) drove natural gas and crude oil to record levels, while coal production has declined steadily as power plants switch to cheaper gas and renewables.',
		caveats: 'Units differ by fuel type: coal (short tons), natural gas (million cubic feet), crude oil (thousand barrels). When "All Fuels" is selected, values are indexed to the first available year (= 100) to enable fair cross-fuel comparison despite different units.',
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
				color: '#a6611a',
			}));
	})());

	const barUnit = $derived(
		barFuel === 'Coal' ? 'short tons' : barFuel === 'Natural Gas' ? 'million cu ft' : 'thousand barrels'
	);

	// Chart 3: Fossil fuel generation over time (from generation data)
	const GEN_FUEL_COLORS: Record<string, string> = {
		Coal: '#4a4a4a',
		'Natural Gas': '#e86c3a',
		Petroleum: '#a6611a',
	};

	const fuelGenSeries: DataSeries[] = $derived((() => {
		const fossilSources = ['Coal', 'Natural Gas', 'Petroleum'];
		return fossilSources.map((source) => ({
			name: source,
			color: GEN_FUEL_COLORS[source] ?? '#999',
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
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'How much electricity does each fossil fuel generate? Coal-fired generation has declined sharply since its peak around 2007, while natural gas generation has surged. Petroleum (oil) plays a minimal and declining role in US electricity generation.',
		caveats: 'Generation data represents net generation at utility-scale power plants. Combined heat and power (CHP) facilities are included. Some natural gas generation comes from plants that can also burn oil as backup fuel.',
	};

	// Chart 4: US Petroleum Trade (Imports, Exports, Net Imports)
	const TRADE_COLORS: Record<string, string> = {
		Imports: '#e31a1c',
		Exports: '#2166ac',
		'Net Imports': '#1b9e77',
	};

	const tradeSeries: DataSeries[] = $derived((() => {
		const petTrade = data.trade
			.filter((d: any) => d.fuel === 'Petroleum' && d.year >= 2000)
			.sort((a: any, b: any) => a.year - b.year);

		return [
			{
				name: 'Imports',
				color: TRADE_COLORS['Imports'],
				values: petTrade.map((d: any) => ({ date: d.year, value: d.imports })),
			},
			{
				name: 'Exports',
				color: TRADE_COLORS['Exports'],
				values: petTrade.map((d: any) => ({ date: d.year, value: d.exports })),
			},
			{
				name: 'Net Imports',
				color: TRADE_COLORS['Net Imports'],
				values: petTrade.map((d: any) => ({ date: d.year, value: d.net_imports })),
			},
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
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'The US was a major net petroleum importer for decades, but the shale revolution and increased domestic production have dramatically reduced net imports. Since roughly 2020 the US has been close to energy self-sufficiency in petroleum, with exports rising sharply even as imports have moderated.',
		caveats: 'Includes crude oil and finished petroleum products. Net imports = imports minus exports. A negative net imports value indicates the US is a net exporter. Data from EIA petroleum movement series.',
	};

	// Chart 5: US Natural Gas Trade
	const gasTradeSeries: DataSeries[] = $derived((() => {
		const gasTrade = data.trade
			.filter((d: any) => d.fuel === 'Natural Gas' && d.year >= 2000)
			.sort((a: any, b: any) => a.year - b.year);
		return [
			{ name: 'Imports', color: '#e31a1c', values: gasTrade.map((d: any) => ({ date: d.year, value: d.imports })) },
			{ name: 'Exports', color: '#2166ac', values: gasTrade.map((d: any) => ({ date: d.year, value: d.exports })) },
			{ name: 'Net Imports', color: '#1b9e77', values: gasTrade.map((d: any) => ({ date: d.year, value: d.net_imports })) },
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
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'The US was a net natural gas importer for decades, relying on pipeline imports from Canada. The shale revolution unlocked vast domestic gas reserves, and the buildout of LNG export terminals transformed the US into a net gas exporter by around 2017 — a historic reversal.',
		caveats: 'Includes pipeline trade (primarily with Canada and Mexico) and LNG shipments. Net imports = imports minus exports. A negative net imports value indicates the US is a net exporter.',
	};

	// Key figures
	const kfTopProducer = $derived(stateRanking.length > 0 ? stateRanking[0].label : '—');
	const kfNumFuels = 3; // Coal, Natural Gas, Crude Oil

	const barMeta: ChartMeta = $derived({
		title: `Top 10 ${barFuel} Producing States (${latestYear})`,
		subtitle: barUnit,
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/',
		unit: barUnit,
		lastUpdated: new Date().toISOString().split('T')[0],
		description: `Fossil fuel production is highly concentrated geographically. ${barFuel === 'Coal' ? 'Wyoming alone produces roughly 40% of US coal, primarily from Powder River Basin surface mines.' : barFuel === 'Natural Gas' ? 'Texas and Pennsylvania lead natural gas production, driven by the Permian Basin and Marcellus Shale respectively.' : 'Texas dominates crude oil production, followed by New Mexico (Permian Basin) and North Dakota (Bakken formation).'}`,
		caveats: 'State-level production data may include estimates for months not yet reported. Rankings can shift year-to-year based on market conditions and weather.',
	});
</script>

<svelte:head>
	<title>Fossil Fuels — US Energy Data</title>
</svelte:head>

<div>
	<header>
		<h1 class="text-2xl font-bold tracking-tight text-text font-display">Fossil Fuels</h1>
		<p class="mt-1 max-w-3xl text-base leading-relaxed text-text-secondary">
			How much fossil fuel does the US actually produce?
		</p>
	</header>

	<!-- Key Figures -->
	<div class="key-figures">
		<div class="key-figure">
			<span class="kf-value" style="color: #a6611a">{kfNumFuels}</span>
			<span class="kf-label">fuel types tracked</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #a6611a">2x</span>
			<span class="kf-label">gas growth since '08</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #a6611a">{kfTopProducer.slice(0, 7)}</span>
			<span class="kf-label">top {barFuel.toLowerCase()} state</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #a6611a">{latestYear}</span>
			<span class="kf-label">latest year</span>
		</div>
	</div>

	<!-- Chart 1: Production trends (hero chart) -->
	<section class="mt-4">
		<div class="mb-2 rounded-xl border border-border bg-surface-alt/50 px-4 py-2.5">
			<div class="flex flex-wrap items-end gap-4">
				<Dropdown
					options={fuelOptions}
					value={selectedFuel}
					label="Fuel Type"
					onchange={(v) => selectedFuel = v}
				/>
				<StateSelect
					selected={selectedStates}
					onchange={(states) => updateConfig('state', states)}
				/>
				<TimeRangeSlider {startYear} {endYear} />
			</div>
		</div>

		<ChartWrapper meta={lineMeta} hero category="Fuels" categoryColor="#a6611a" data={timeFilteredCombined.flatMap((s) => s.values.map((v) => ({ fuel: s.name, year: v.date, production: v.value })))}>
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
			<p class="mt-3 text-sm text-text-muted">
				Values indexed to first available year (= 100) to enable comparison across fuels with different units.
			</p>
		{/if}
	</section>

	<!-- Chart 2: Top producing states -->
	<section class="-mx-6 bg-surface-alt px-6 py-6 sm:-mx-8 sm:px-8 md:rounded-xl mt-6">
		<ChartWrapper meta={barMeta} category="Fuels" categoryColor="#a6611a" data={stateRanking.map((d) => ({ state: d.label, production: d.value }))}>
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

	<!-- Insight -->
	<div class="insight-card my-4">
		<div class="flex items-start gap-4">
			<div class="flex-shrink-0">
				<span class="text-xl font-bold text-accent" style="font-family: var(--font-mono)">2x</span>
				<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">gas growth</span>
			</div>
			<p class="text-base leading-relaxed text-text-secondary">
				US natural gas production has roughly doubled since 2008, while coal output has declined by nearly half — a seismic shift driven by the shale revolution.
			</p>
		</div>
	</div>

	<!-- Chart 3: Fossil fuel generation -->
	<section class="mt-8">
		<ChartWrapper meta={fuelGenMeta} category="Fuels" categoryColor="#a6611a" data={timeFilteredFuelGen.flatMap((s) => s.values.map((v) => ({ fuel: s.name, year: v.date, generation: v.value })))}>
			<LineChart
				series={timeFilteredFuelGen}
				xLabel="Year"
				yLabel="thousand MWh"
				yFormat={formatCompact}
				unit="thousand MWh"
			/>
		</ChartWrapper>

		<!-- Cross-link -->
		<p class="mt-4 text-sm">
			<a href="/generation" class="text-accent/80 hover:text-accent transition-colors no-underline">See how these fuels translate into electricity generation &rarr;</a>
		</p>
	</section>

	<!-- Chart 4: US Petroleum Trade -->
	<section class="-mx-6 bg-surface-alt px-6 py-6 sm:-mx-8 sm:px-8 md:rounded-xl mt-6">
		<ChartWrapper meta={tradeMeta} category="Fuels" categoryColor="#a6611a" data={timeFilteredTrade.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, value: v.value })))}>
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

	<!-- Chart 5: US Natural Gas Trade -->
	<section class="mt-8">
		<ChartWrapper meta={gasTradeMeta} category="Fuels" categoryColor="#a6611a" data={timeFilteredGasTrade.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, value: v.value })))}>
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
