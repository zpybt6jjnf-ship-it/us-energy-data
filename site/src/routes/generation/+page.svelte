<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import BarChart from '$components/charts/BarChart.svelte';
	import DivergingBarChart from '$components/charts/DivergingBarChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { ENERGY_SOURCE_COLORS, CHART_COLORS_CSS, CATEGORY_COLORS, STORAGE_COLOR, CARBON_INTENSITY_COLOR } from '$utils/colors';
	import { stateFips, stateFromAbbr } from '$utils/states';
	import { formatCompact } from '$utils/formatting';
	import { chartConfig, updateConfig, toggleState, hasActiveFilters, resetConfig } from '$stores/chartConfig';
	import { interpolateGreens } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const shareAnnotations = [
		{ date: 2007, label: 'Shale boom' },
		{ date: 2015, label: 'Clean Power Plan' },
		{ date: 2022, label: 'IRA' },
	];

	const carbonAnnotations = [
		{ date: 2007, label: 'Shale boom' },
		{ date: 2022, label: 'IRA' },
	];

	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	const startYear = $derived($chartConfig.startYear);
	const endYear = $derived($chartConfig.endYear);

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
		lastUpdated: data.lastUpdated,
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

	const timeFilteredTrend = $derived(
		trendSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const lineMeta: ChartMeta = {
		title: 'Generation Share by Source Over Time',
		subtitle: 'Percentage of total US generation',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: data.lastUpdated,
		description: 'The share of coal in US electricity generation has fallen dramatically since 2008, replaced largely by natural gas (due to the shale gas revolution) and wind/solar (driven by falling costs and policy incentives).',
		caveats: 'Shares are calculated as percentage of total net generation. Hydro share fluctuates with annual precipitation. Solar includes both utility-scale and estimated distributed generation.',
	};

	// Line chart: Fossil vs Nuclear vs Renewable generation shares
	const FOSSIL_SOURCES = ['Coal', 'Natural Gas', 'Petroleum'];
	const NUCLEAR_SOURCES = ['Nuclear'];
	const RENEWABLE_SOURCES = ['Wind', 'Solar', 'Hydro', 'Geothermal'];

	const fossilVsCleanSeries: DataSeries[] = $derived((() => {
		const categories = [
			{ name: 'Fossil', sources: FOSSIL_SOURCES, color: CATEGORY_COLORS.Fossil },
			{ name: 'Nuclear', sources: NUCLEAR_SOURCES, color: CATEGORY_COLORS.Nuclear },
			{ name: 'Renewable', sources: RENEWABLE_SOURCES, color: CATEGORY_COLORS.Renewable },
		];

		const totalByYear = new Map<number, number>();
		for (const d of data.national) {
			totalByYear.set(d.year, (totalByYear.get(d.year) ?? 0) + d.generation);
		}

		return categories.map(({ name, sources, color }) => {
			const catByYear = new Map<number, number>();
			for (const d of data.national) {
				if (sources.includes(d.source)) {
					catByYear.set(d.year, (catByYear.get(d.year) ?? 0) + d.generation);
				}
			}
			const values = [...catByYear.entries()]
				.map(([year, gen]) => {
					const total = totalByYear.get(year) ?? 1;
					return { date: year, value: (gen / total) * 100 };
				})
				.sort((a, b) => a.date - b.date);
			return { name, color, values };
		}).filter((s) => s.values.length > 0);
	})());

	const timeFilteredFossilVsClean = $derived(
		fossilVsCleanSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const fossilVsCleanMeta: ChartMeta = {
		title: 'Fossil vs Nuclear vs Renewable Generation',
		subtitle: 'Percentage of total US generation',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: data.lastUpdated,
		description: 'The big-picture energy transition: fossil fuels still dominate US electricity but their share has fallen steadily since the mid-2000s as renewables have surged. Nuclear has held a remarkably stable ~20% share for decades, acting as a zero-carbon bridge. The Inflation Reduction Act (2022) is expected to accelerate the renewable buildout further.',
		caveats: 'Fossil includes coal, natural gas, and petroleum. Renewable includes wind, solar, hydro, and geothermal. Shares are computed from generation data and may not sum to exactly 100% due to minor "other" sources not categorized here.',
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
				color: CHART_COLORS_CSS[(genTrendSourceSeries.length + i) % CHART_COLORS_CSS.length],
				values: [...total.entries()]
					.map(([year, value]) => ({ date: year, value }))
					.sort((a, b) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const genTrendSeries: DataSeries[] = $derived([...genTrendSourceSeries, ...stateGenSeries]);

	const timeFilteredGenTrend = $derived(
		genTrendSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const genTrendMeta: ChartMeta = {
		title: 'Generation Volume by Source Over Time',
		subtitle: 'Thousand megawatt-hours, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'thousand MWh',
		lastUpdated: data.lastUpdated,
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
		lastUpdated: data.lastUpdated,
		description: 'Natural gas dominates US installed capacity, followed by coal and wind. Wind capacity has grown rapidly and now exceeds nuclear. Solar capacity is growing fast but is not yet tracked in this dataset.',
		caveats: 'Capacity values represent net summer capacity and do not reflect actual generation, which depends on capacity factors. Note: EIA Form 860 reporting changed in 2008, causing an apparent doubling of some categories (especially natural gas) — this reflects reclassification, not real construction. Solar may be underrepresented due to distributed generation not included in utility-scale data.',
	});

	// Line chart: Carbon intensity over time
	const carbonSeries: DataSeries[] = $derived([
		{
			name: 'Carbon Intensity',
			color: CARBON_INTENSITY_COLOR,
			values: data.carbonIntensity
				.map((d: any) => ({ date: d.year, value: d.carbon_intensity_kg_per_mwh }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const timeFilteredCarbon = $derived(
		carbonSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const carbonMeta: ChartMeta = {
		title: 'Carbon Intensity of US Electricity',
		subtitle: 'kg CO\u2082 per MWh',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'kg CO₂/MWh',
		lastUpdated: data.lastUpdated,
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
		lastUpdated: data.lastUpdated,
		description: 'Renewable energy penetration varies dramatically by state. Washington and Oregon lead with hydropower, while Iowa and Kansas have high wind shares. Southern states lag due to greater reliance on natural gas and coal.',
		caveats: 'Renewables include wind, solar, and conventional hydroelectric. Nuclear is excluded despite being zero-carbon. Biomass is not included in this calculation.',
	});

	// Chart 7: Capacity Factors by Technology Over Time
	const CF_SOURCES = ['Coal', 'Hydro', 'Natural Gas', 'Nuclear', 'Petroleum', 'Wind'];
	// Generation is in thousand MWh, capacity is in MW → multiply by 1000 to convert to MWh
	const CF_CORRECTION = 1000;
	const CF_START_YEAR = 2010;

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
					values.push({ date: year, value: cf });
				}
			}
			return {
				name: source,
				color: ENERGY_SOURCE_COLORS[source.toLowerCase()] ?? '#999',
				values: values.sort((a, b) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const timeFilteredCapFactor = $derived(
		capacityFactorSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const capacityFactorMeta: ChartMeta = {
		title: 'Capacity Factors by Technology Over Time',
		subtitle: 'Actual generation as % of theoretical maximum',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '%',
		lastUpdated: data.lastUpdated,
		description: 'Nuclear has the highest capacity factor (~90%), reflecting its role as always-on baseload power. Natural gas capacity factors have risen as gas displaced coal for baseload generation. Coal capacity factors have declined as plants run less frequently. Wind and hydro are lower and more variable, driven by weather.',
		caveats: 'Capacity factors are computed from annual generation and installed capacity data. Values above 100% are capped. Wind and hydro capacity factors vary with weather conditions. Solar is excluded because capacity data for solar is incomplete in this dataset.',
	};

	// Chart 8: Net Capacity Additions by Source
	const capChangeSources = ['Coal', 'Natural Gas', 'Wind', 'Nuclear', 'Hydro', 'Petroleum'];
	const CAP_CHANGE_START_YEAR = 2005;

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

	const capChangeAggregate = $derived((() => {
		const timeFilteredCapChange = capChangeSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}));
		const yearTotals = new Map<number, number>();
		for (const s of timeFilteredCapChange) {
			for (const v of s.values) {
				yearTotals.set(v.date, (yearTotals.get(v.date) ?? 0) + v.value);
			}
		}
		return [...yearTotals.entries()]
			.sort((a, b) => a[0] - b[0])
			.map(([year, value]) => ({ label: String(year), value }));
	})());

	const capChangeMeta: ChartMeta = {
		title: 'Net Capacity Additions by Source',
		subtitle: 'Year-over-year change in installed capacity, MW',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/state/',
		unit: 'MW',
		lastUpdated: data.lastUpdated,
		description: 'Wind and natural gas have dominated new capacity additions since the mid-2000s. Coal has seen consistent net retirements since 2011 as older plants close. Nuclear capacity has been roughly flat, with new builds barely offsetting closures.',
		caveats: 'Values represent net change in installed capacity (additions minus retirements). Negative values indicate net retirements. Solar is not shown because it is tracked under a separate energy source category in the EIA capability dataset.',
	};

	// Chart 9: Battery Storage Capacity
	const storageSeries: DataSeries[] = $derived([
		{
			name: 'Battery Storage',
			color: STORAGE_COLOR,
			values: data.storage
				.map((d: any) => ({ date: d.year, value: d.capacity_mw }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const timeFilteredStorage = $derived(
		storageSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const storageMeta: ChartMeta = {
		title: 'US Battery Storage Capacity',
		subtitle: 'Net summer capacity, megawatts',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/state/',
		unit: 'MW',
		lastUpdated: data.lastUpdated,
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
	<!-- Title + intro -->
	<div class="prose-width">
		<h1 class="text-2xl font-display mb-4">Generation & Resources</h1>
		<p class="narrative-text">America's power grid is in the middle of a generational transition. Natural gas now provides roughly <span class="inline-stat">{Math.round(kfGasShare)}%</span> of electricity, overtaking coal which has fallen to <span class="inline-stat">{Math.round(kfCoalShare)}%</span>. Renewables — wind, solar, and hydro — account for <span class="inline-stat">{Math.round(kfRenewShare)}%</span> and growing.</p>
	</div>

	<!-- Section: What powers the grid today? -->
	<div class="prose-width">
		<h2 class="section-heading" id="generation-mix">What powers the grid today?</h2>
		<p class="narrative-text">The United States generated over 4 trillion kilowatt-hours of electricity in {latestYear}. Natural gas has been the single largest source since 2016, but the full picture is more nuanced — nuclear still provides a fifth of all power, and wind has overtaken hydro as the leading renewable.</p>
	</div>

	<div class="chart-breakout">
		<section>
			<ChartWrapper meta={barMeta} hero data={sourceBreakdown.map((d: any) => ({ source: d.label, generation: d.value }))}>
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
	</div>

	<!-- Section: How fast is the energy mix changing? -->
	<div class="prose-width">
		<h2 class="section-heading">How fast is the energy mix changing?</h2>
		<p class="narrative-text">The shift away from coal has been remarkably fast by the standards of energy systems. In absolute terms, natural gas generation has more than doubled since 2000, while coal has roughly halved. Wind and solar are growing from a smaller base but their trajectory is steep.</p>
	</div>

	<div class="chart-breakout">
		<section>
			<ChartWrapper meta={genTrendMeta} data={timeFilteredGenTrend.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, generation: v.value })))}>
				{#snippet controls()}
					<StateSelect
						selected={selectedStates}
						onchange={(states) => updateConfig('state', states)}
						label=""
						compact
					/>
					<TimeRangeSlider {startYear} {endYear} />
					{#if hasActiveFilters($chartConfig)}
						<button onclick={resetConfig} class="text-xs text-text-muted hover:text-accent transition-colors">Reset</button>
					{/if}
				{/snippet}
				<LineChart
					series={timeFilteredGenTrend}
					xLabel="Year"
					yLabel="thousand MWh"
					yFormat={formatCompact}
					unit="thousand MWh"
				/>
			</ChartWrapper>
		</section>
	</div>

	<div class="prose-width">
		<div class="insight-card">
			<div class="flex items-start gap-4">
				<div class="flex-shrink-0">
					<span class="text-xl font-bold text-accent" style="font-family: var(--font-mono)">50→16%</span>
					<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">coal decline</span>
				</div>
				<p class="text-sm leading-relaxed text-text-secondary">
					Coal's share of US electricity has fallen from 50% to roughly 16% in under two decades — replaced mostly by natural gas and renewables.
				</p>
			</div>
		</div>
	</div>

	<div class="chart-breakout">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={lineMeta} data={timeFilteredTrend.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, share: v.value })))}>
					<LineChart
						series={timeFilteredTrend}
						xLabel="Year"
						yLabel="% of total"
						yFormat={format(',.1f')}
						unit="%"
						annotations={shareAnnotations}
					/>
				</ChartWrapper>
			</section>

			<section>
				<ChartWrapper meta={fossilVsCleanMeta} data={timeFilteredFossilVsClean.flatMap((s) => s.values.map((v) => ({ category: s.name, year: v.date, share: v.value })))}>
					<LineChart
						series={timeFilteredFossilVsClean}
						xLabel="Year"
						yLabel="% of total"
						yFormat={format(',.1f')}
						unit="%"
						annotations={shareAnnotations}
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Section: Where are renewables growing fastest? -->
	<div class="prose-width">
		<h2 class="section-heading">Where are renewables growing fastest?</h2>
		<p class="narrative-text">Renewable energy adoption varies enormously across the country. States with strong wind resources in the Great Plains and hydropower in the Pacific Northwest lead, while the Southeast still relies heavily on gas and nuclear. Policy, geography, and legacy infrastructure all shape the map.</p>
	</div>

	<div class="chart-breakout">
		<section>
			<ChartWrapper meta={mapMeta} data={mapData.map((d: any) => ({ state: d.state, renewable_share: d.value }))}>
				<ChoroplethMap
					data={mapData}
					topology={data.topology}
					colorInterpolator={interpolateGreens}
					valueFormat={format(',.1f')}
					unit="%"
					onStateClick={toggleState}
				/>
			</ChartWrapper>
			{#if selectedStates.length > 0}
				<p class="text-xs text-text-muted mt-1">National data — not affected by state selection</p>
			{/if}
		</section>
	</div>

	<!-- Cross-link to fuels -->
	<p class="prose-width mt-8">
		<a href="/fuels" class="text-accent hover:text-accent-light no-underline font-medium">Where do these fuels come from? Explore fossil fuel production →</a>
	</p>

	<!-- Section: How much capacity is being built? -->
	<div class="prose-width">
		<h2 class="section-heading" id="capacity">How much capacity is being built?</h2>
		<p class="narrative-text">Installed capacity tells a different story from generation. A gigawatt of wind or solar produces less electricity per year than a gigawatt of nuclear, because the wind doesn't always blow and the sun doesn't always shine. Capacity factors — the ratio of actual output to theoretical maximum — explain the gap.</p>
	</div>

	<div class="chart-breakout">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={capacityMeta} data={capacityBreakdown.map((d: any) => ({ source: d.label, capacity_mw: d.value }))}>
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
				<ChartWrapper meta={capacityFactorMeta} data={timeFilteredCapFactor.flatMap((s) => s.values.map((v) => ({ source: s.name, year: v.date, capacity_factor_pct: v.value })))}>
					<LineChart
						series={timeFilteredCapFactor}
						xLabel="Year"
						yLabel="%"
						yFormat={format(',.0f')}
						unit="%"
						includeZero={false}
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Section: What is being added and retired? -->
	<div class="prose-width">
		<h2 class="section-heading">What is being added and retired?</h2>
		<p class="narrative-text">New power plants are overwhelmingly wind and natural gas. Meanwhile, coal retirements have accelerated — the fleet is aging and can't compete on cost. Battery storage, nearly nonexistent a decade ago, is scaling fast as costs plunge and states mandate grid-scale storage to back up intermittent renewables.</p>
	</div>

	<div class="chart-breakout">
		<div class="grid md:grid-cols-2 gap-6">
			<section>
				<ChartWrapper meta={capChangeMeta} data={capChangeAggregate.map((d) => ({ year: d.label, net_change_mw: d.value }))}>
					<DivergingBarChart
						data={capChangeAggregate}
						yLabel="MW"
						yFormat={formatCompact}
						unit="MW"
					/>
				</ChartWrapper>
			</section>

			<section>
				<ChartWrapper meta={storageMeta} data={timeFilteredStorage[0].values.map((v) => ({ year: v.date, capacity_mw: v.value }))}>
					<LineChart
						series={timeFilteredStorage}
						xLabel="Year"
						yLabel="MW"
						yFormat={formatCompact}
						unit="MW"
					/>
				</ChartWrapper>
			</section>
		</div>
	</div>

	<!-- Section: Is the grid getting cleaner? -->
	<div class="prose-width">
		<h2 class="section-heading" id="decarbonization">Is the grid getting cleaner?</h2>
		<p class="narrative-text">Carbon intensity — the CO₂ emitted per unit of electricity — is the bottom-line metric for grid decarbonization. It has fallen steadily since the mid-2000s as gas displaced coal and renewables grew. The shale gas revolution and the Inflation Reduction Act mark the two biggest inflection points.</p>
	</div>

	<div class="chart-breakout">
		<section>
			<ChartWrapper meta={carbonMeta} data={timeFilteredCarbon[0].values.map((v) => ({ year: v.date, carbon_intensity_kg_per_mwh: v.value }))}>
				<LineChart
					series={timeFilteredCarbon}
					xLabel="Year"
					yLabel="kg CO₂/MWh"
					yFormat={format(',.0f')}
					unit="kg CO₂/MWh"
					annotations={carbonAnnotations}
					includeZero={false}
				/>
			</ChartWrapper>
		</section>
	</div>
</div>
