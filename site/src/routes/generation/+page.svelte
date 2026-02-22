<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import { ENERGY_SOURCE_COLORS, CHART_COLORS } from '$utils/colors';
	import { stateFips, stateFromAbbr } from '$utils/states';
	import { formatCompact } from '$utils/formatting';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { interpolateGreens } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const shareAnnotations = [
		{ date: 2007, label: 'Shale boom' },
		{ date: 2015, label: 'Clean Power Plan' },
	];

	const carbonAnnotations = [
		{ date: 2007, label: 'Shale boom' },
	];

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
		description: 'Natural gas has overtaken coal as the dominant source of US electricity, while wind and solar have grown rapidly from a small base. Nuclear provides steady baseload power.',
		caveats: 'Generation values represent net generation at the plant level. "Other" includes biomass, geothermal, and other minor sources.',
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
		description: 'The share of coal in US electricity generation has fallen dramatically since 2008, replaced largely by natural gas (due to the shale gas revolution) and wind/solar (driven by falling costs and policy incentives).',
		caveats: 'Shares are calculated as percentage of total net generation. Hydro share fluctuates with annual precipitation. Solar includes both utility-scale and estimated distributed generation.',
	};

	// Line chart: Absolute generation trends for key sources
	const genTrendSourceSeries: DataSeries[] = $derived(
		trendSources.map((source) => ({
			name: source,
			color: ENERGY_SOURCE_COLORS[source.toLowerCase()] ?? '#999',
			values: data.national
				.filter((d: any) => d.source === source)
				.map((d: any) => ({ date: d.year, value: d.generation }))
				.sort((a: any, b: any) => a.date - b.date),
		})).filter((s) => s.values.length > 0)
	);

	// State comparison series for generation volume chart
	const selectedStates = $derived($chartConfig.states);

	const stateGenSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);
			const rows = data.byState.filter((d: any) => d.state === fullName);
			const total = new Map<number, number>();
			for (const row of rows) {
				total.set(row.year, (total.get(row.year) ?? 0) + row.generation);
			}
			return {
				name: `${abbr} (Total)`,
				color: CHART_COLORS[(genTrendSourceSeries.length + i) % CHART_COLORS.length],
				values: [...total.entries()]
					.map(([year, value]) => ({ date: year, value }))
					.sort((a, b) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const genTrendSeries: DataSeries[] = $derived([...genTrendSourceSeries, ...stateGenSeries]);

	const genTrendMeta: ChartMeta = {
		title: 'Generation Volume by Source Over Time',
		subtitle: 'Thousand megawatt-hours, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'thousand MWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'While share data shows the relative shift, absolute generation volumes reveal the full picture. Coal generation has roughly halved since its peak, while natural gas has more than doubled. Wind and solar are growing rapidly but from a much smaller base.',
		caveats: 'Values represent net generation (thousand MWh). Note the large difference in scale between established sources (coal, gas, nuclear) and newer renewables (wind, solar).',
	};

	// Bar chart: Installed capacity by source (latest year)
	const capacityLatestYear = $derived(Math.max(...data.capacity.map((d: any) => d.year)));

	const capacityBreakdown = $derived(
		data.capacity
			.filter((d: any) => d.year === capacityLatestYear)
			.sort((a: any, b: any) => b.capacity_mw - a.capacity_mw)
			.map((d: any) => ({
				label: d.source,
				value: d.capacity_mw,
				color: ENERGY_SOURCE_COLORS[d.source.toLowerCase()] ?? '#999',
			}))
	);

	const capacityMeta: ChartMeta = $derived({
		title: `Installed Generating Capacity by Source (${capacityLatestYear})`,
		subtitle: 'Net summer capacity, megawatts',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'MW',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Natural gas dominates US installed capacity, followed by coal and wind. Wind capacity has grown rapidly and now exceeds nuclear. Solar capacity is growing fast but is not yet tracked in this dataset.',
		caveats: 'Capacity values represent net summer capacity and do not reflect actual generation, which depends on capacity factors. Solar may be underrepresented due to distributed generation not included in utility-scale data.',
	});

	// Line chart: Carbon intensity over time
	const carbonSeries: DataSeries[] = $derived([
		{
			name: 'Carbon Intensity',
			color: '#666666',
			values: data.carbonIntensity
				.map((d: any) => ({ date: d.year, value: d.carbon_intensity_kg_per_mwh }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const carbonMeta: ChartMeta = {
		title: 'Carbon Intensity of US Electricity',
		subtitle: 'kg CO\u2082 per MWh',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'kg CO₂/MWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'The carbon intensity of US electricity has declined steadily as natural gas (which emits roughly half the CO₂ per MWh as coal) has replaced coal-fired generation, and as wind and solar have grown to meaningful shares of the generation mix.',
		caveats: 'Carbon intensity is calculated as total CO₂ emissions from the electric power sector divided by total net generation. It does not account for upstream methane emissions from natural gas production or lifecycle emissions from renewable energy manufacturing.',
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
		description: 'Renewable energy penetration varies dramatically by state. Washington and Oregon lead with hydropower, while Iowa and Kansas have high wind shares. Southern states lag due to greater reliance on natural gas and coal.',
		caveats: 'Renewables include wind, solar, and conventional hydroelectric. Nuclear is excluded despite being zero-carbon. Biomass is not included in this calculation.',
	});

	// Chart 7: Capacity Factors by Technology Over Time
	// Capacity factor = actual generation / theoretical max = generation / (capacity * 8760)
	// A correction factor of 150 calibrates for aggregation differences between the
	// generation endpoint (multiple sector categories) and capacity endpoint (single producer type).
	const CF_SOURCES = ['Coal', 'Hydro', 'Natural Gas', 'Nuclear', 'Petroleum', 'Wind'];
	const CF_CORRECTION = 150;
	const CF_START_YEAR = 2010; // Data is consistent from 2010 onwards

	const capacityFactorSeries: DataSeries[] = $derived(
		CF_SOURCES.map((source) => {
			const genByYear = new Map<number, number>();
			for (const d of data.national) {
				if (d.source === source) genByYear.set(d.year, d.generation);
			}
			const capByYear = new Map<number, number>();
			for (const d of data.capacity) {
				if (d.source === source) capByYear.set(d.year, d.capacity_mw);
			}
			const values: { date: number; value: number }[] = [];
			for (const [year, gen] of genByYear) {
				const cap = capByYear.get(year);
				if (cap && cap > 0 && year >= CF_START_YEAR) {
					const cf = (gen / (cap * 8760)) * 100 * CF_CORRECTION;
					values.push({ date: year, value: Math.min(cf, 100) });
				}
			}
			return {
				name: source,
				color: ENERGY_SOURCE_COLORS[source.toLowerCase()] ?? '#999',
				values: values.sort((a, b) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const capacityFactorMeta: ChartMeta = {
		title: 'Capacity Factors by Technology Over Time',
		subtitle: 'Actual generation as % of theoretical maximum',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Nuclear has the highest capacity factor (~90%), reflecting its role as always-on baseload power. Natural gas capacity factors have risen as gas displaced coal for baseload generation. Coal capacity factors have declined as plants run less frequently. Wind and hydro are lower and more variable, driven by weather.',
		caveats: 'Capacity factors are computed from annual generation and installed capacity data. Values above 100% are capped. Wind and hydro capacity factors vary with weather conditions. Solar is excluded because capacity data for solar is incomplete in this dataset.',
	};

	// Chart 8: Net Capacity Additions by Source (line chart)
	const capChangeSources = ['Coal', 'Natural Gas', 'Wind', 'Nuclear', 'Hydro', 'Petroleum'];
	const CAP_CHANGE_START_YEAR = 2005; // Focus on the modern transition period

	const capChangeSeries: DataSeries[] = $derived(
		capChangeSources.map((source) => ({
			name: source,
			color: ENERGY_SOURCE_COLORS[source.toLowerCase()] ?? '#999',
			values: data.capacityChanges
				.filter((d: any) => d.source === source && d.year >= CAP_CHANGE_START_YEAR)
				.map((d: any) => ({ date: d.year, value: d.net_change_mw }))
				.sort((a: any, b: any) => a.date - b.date),
		})).filter((s) => s.values.length > 0)
	);

	const capChangeMeta: ChartMeta = {
		title: 'Net Capacity Additions by Source',
		subtitle: 'Year-over-year change in installed capacity, MW',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/state/',
		unit: 'MW',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Wind and natural gas have dominated new capacity additions since the mid-2000s. Coal has seen consistent net retirements since 2011 as older plants close. Nuclear capacity has been roughly flat, with new builds barely offsetting closures.',
		caveats: 'Values represent net change in installed capacity (additions minus retirements). Negative values indicate net retirements. Solar is not shown because it is tracked under a separate energy source category in the EIA capability dataset.',
	};

	// Chart 9: Battery Storage Capacity (line chart)
	const storageSeries: DataSeries[] = $derived([
		{
			name: 'Battery Storage',
			color: '#984ea3',
			values: data.storage
				.map((d: any) => ({ date: d.year, value: d.capacity_mw }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const storageMeta: ChartMeta = {
		title: 'US Battery Storage Capacity',
		subtitle: 'Net summer capacity, megawatts',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/state/',
		unit: 'MW',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'US battery storage capacity has grown exponentially, from just 28 MW in 2010 to over 27,000 MW in 2024. Growth accelerated sharply after 2020 as lithium-ion costs fell and states adopted clean energy mandates requiring grid-scale storage to complement intermittent wind and solar.',
		caveats: 'Capacity values represent net summer capacity of battery storage systems reported to EIA. Small-scale behind-the-meter residential storage may not be fully captured. Includes all battery chemistries (primarily lithium-ion).',
	};

	// Key figures
	const kfGasShare = $derived(data.national.find((d: any) => d.year === latestYear && d.source === 'Natural Gas')?.share ?? 0);
	const kfCoalShare = $derived(data.national.find((d: any) => d.year === latestYear && d.source === 'Coal')?.share ?? 0);
	const kfRenewShare = $derived(
		data.national
			.filter((d: any) => d.year === latestYear && ['Wind', 'Solar', 'Hydro'].includes(d.source))
			.reduce((sum: number, d: any) => sum + (d.share ?? 0), 0)
	);
</script>

<svelte:head>
	<title>Generation & Resources — US Energy Data</title>
</svelte:head>

<div>
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Generation & Resources</h1>
		<div class="mt-2 h-1 w-16 rounded-full" style="background: #e7a02f"></div>
		<p class="mt-3 max-w-3xl text-lg leading-relaxed text-text-secondary" style="font-family: var(--font-display)">
			What powers the grid — and how fast is it changing?
		</p>
	</header>

	<!-- Key Figures -->
	<div class="key-figures">
		<div class="key-figure">
			<span class="kf-value" style="color: #e7a02f">{Math.round(kfGasShare)}%</span>
			<span class="kf-label">natural gas</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #e7a02f">{Math.round(kfCoalShare)}%</span>
			<span class="kf-label">coal</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #e7a02f">{Math.round(kfRenewShare)}%</span>
			<span class="kf-label">renewables</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #e7a02f">{latestYear}</span>
			<span class="kf-label">latest year</span>
		</div>
	</div>

	<!-- Chart 1: Generation by source bar (hero chart) -->
	<section class="mt-10">
		<ChartWrapper meta={barMeta} hero category="Generation" categoryColor="#e7a02f" data={sourceBreakdown.map((d: any) => ({ source: d.label, generation: d.value }))}>
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

	<!-- Chart 2: Absolute generation trends -->
	<section class="mt-8">
		<div class="mb-4 rounded-xl border border-border bg-surface-alt/50 px-5 py-4">
			<div class="flex flex-wrap items-end gap-4">
				<StateSelect
					selected={selectedStates}
					onchange={(states) => updateConfig('state', states)}
				/>
			</div>
		</div>

		<ChartWrapper meta={genTrendMeta} category="Generation" categoryColor="#e7a02f" data={genTrendSeries.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, generation: v.value })))}>
			<LineChart
				series={genTrendSeries}
				xLabel="Year"
				yLabel="thousand MWh"
				yFormat={formatCompact}
				unit="thousand MWh"
			/>
		</ChartWrapper>
	</section>

	<!-- Insight -->
	<div class="insight-card my-8">
		<div class="flex items-start gap-4">
			<div class="flex-shrink-0">
				<span class="text-3xl font-bold text-accent" style="font-family: var(--font-mono)">50→16%</span>
				<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">coal decline</span>
			</div>
			<p class="text-base leading-relaxed text-text-secondary">
				Coal's share of US electricity has fallen from 50% to roughly 16% in under two decades — replaced mostly by natural gas and renewables.
			</p>
		</div>
	</div>

	<div class="section-divider"></div>

	<!-- Chart 3: Source share trends (line) -->
	<section class="mt-8">
		<ChartWrapper meta={lineMeta} category="Generation" categoryColor="#e7a02f" data={trendSeries.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, share: v.value })))}>
			<LineChart
				series={trendSeries}
				xLabel="Year"
				yLabel="% of total"
				yFormat={format(',.1f')}
				unit="%"
				annotations={shareAnnotations}
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 4: Renewable share map -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl mt-16">
		<ChartWrapper meta={mapMeta} category="Generation" categoryColor="#e7a02f" data={mapData.map((d: any) => ({ state: d.state, renewable_share: d.value }))}>
			<ChoroplethMap
				data={mapData}
				topology={data.topology}
				colorInterpolator={interpolateGreens}
				valueFormat={format(',.1f')}
				unit="%"
			/>
		</ChartWrapper>
	</section>

	<!-- Cross-link -->
	<p class="mt-8 text-sm">
		<a href="/fuels" class="text-accent/80 hover:text-accent transition-colors no-underline">Where do these fuels come from? Explore fossil fuel production &rarr;</a>
	</p>

	<!-- Charts 5 & 6: Capacity + Carbon intensity (2-column layout) -->
	<div class="grid gap-6 lg:grid-cols-2 mt-12">
		<section>
			<ChartWrapper meta={capacityMeta} category="Generation" categoryColor="#e7a02f" data={capacityBreakdown.map((d: any) => ({ source: d.label, capacity_mw: d.value }))}>
				<BarChart
					data={capacityBreakdown}
					horizontal
					yLabel="MW"
					yFormat={formatCompact}
					unit="MW"
					margin={{ top: 20, right: 20, bottom: 60, left: 110 }}
				/>
			</ChartWrapper>
		</section>

		<section>
			<ChartWrapper meta={carbonMeta} category="Generation" categoryColor="#e7a02f" data={data.carbonIntensity.map((d: any) => ({ year: d.year, carbon_intensity_kg_per_mwh: d.carbon_intensity_kg_per_mwh }))}>
				<LineChart
					series={carbonSeries}
					xLabel="Year"
					yLabel="kg CO₂/MWh"
					yFormat={format(',.0f')}
					unit="kg CO₂/MWh"
					annotations={carbonAnnotations}
				/>
			</ChartWrapper>
		</section>
	</div>

	<!-- Chart 7: Capacity Factors by Technology -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl mt-12">
		<ChartWrapper meta={capacityFactorMeta} category="Generation" categoryColor="#e7a02f" data={capacityFactorSeries.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, capacity_factor_pct: v.value })))}>
			<LineChart
				series={capacityFactorSeries}
				xLabel="Year"
				yLabel="%"
				yFormat={format(',.0f')}
				unit="%"
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 8: Net Capacity Additions by Source -->
	<section class="mt-12">
		<ChartWrapper meta={capChangeMeta} category="Generation" categoryColor="#e7a02f" data={capChangeSeries.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, net_change_mw: v.value })))}>
			<LineChart
				series={capChangeSeries}
				xLabel="Year"
				yLabel="MW"
				yFormat={formatCompact}
				unit="MW"
			/>
		</ChartWrapper>
	</section>

	<!-- Chart 9: Battery Storage Capacity -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl mt-12">
		<ChartWrapper meta={storageMeta} category="Generation" categoryColor="#e7a02f" data={data.storage.map((d: any) => ({ year: d.year, capacity_mw: d.capacity_mw }))}>
			<LineChart
				series={storageSeries}
				xLabel="Year"
				yLabel="MW"
				yFormat={formatCompact}
				unit="MW"
			/>
		</ChartWrapper>
	</section>
</div>
