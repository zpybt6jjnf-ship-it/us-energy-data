<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import TimeRangeSlider from '$components/ui/TimeRangeSlider.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { stateFips, stateFromAbbr } from '$utils/states';
	import { CHART_COLORS } from '$utils/colors';
	import { interpolateYlOrRd } from 'd3-scale-chromatic';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const priceAnnotations = [
		{ date: 2008, label: '08 Recession' },
		{ date: 2020, label: 'COVID-19', labelPosition: 'bottom' as const },
		{ date: 2022, label: 'IRA' },
	];

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

	// State comparison: build state-level series for selected states
	const selectedStates = $derived($chartConfig.states);

	const sectorForState = $derived(
		activeSector === 'all' ? 'residential' : activeSector
	);

	const stateSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			const fullName = stateFromAbbr(abbr);
			const sectorLabel = sectorForState.charAt(0).toUpperCase() + sectorForState.slice(1);
			return {
				name: `${abbr} (${sectorLabel})`,
				color: CHART_COLORS[(filteredSeries.length + i) % CHART_COLORS.length],
				values: data.byState
					.filter((d: any) => d.state === fullName && d.sector === sectorLabel)
					.map((d: any) => ({ date: d.year, value: d.price }))
					.sort((a: any, b: any) => a.date - b.date),
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
		title: 'Retail Electricity Prices by Sector',
		subtitle: 'US national average, cents per kilowatt-hour, annual',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: 'cents/kWh',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Average retail electricity prices vary significantly across sectors. Residential customers typically pay the highest rates due to distribution costs, while industrial users benefit from bulk pricing and direct market access. Use the state selector to compare individual states against the national average.',
		caveats: 'Prices are nominal (not adjusted for inflation). National averages are revenue-weighted across all utilities. Some state-level data may be incomplete for earlier years.',
	};

	// State-level map data: latest year residential prices
	const latestYear = $derived(Math.max(...data.national.map((d: any) => d.year)));

	// Key figures
	const latestRes = $derived(data.national.filter((d: any) => d.year === latestYear && d.sector === 'Residential'));
	const latestInd = $derived(data.national.filter((d: any) => d.year === latestYear && d.sector === 'Industrial'));
	const resPrice = $derived(latestRes.length > 0 ? latestRes[0].price : 0);
	const indPrice = $derived(latestInd.length > 0 ? latestInd[0].price : 0);
	const sectorGap = $derived(indPrice > 0 ? Math.round(((resPrice - indPrice) / indPrice) * 100) : 0);

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
		description: 'Electricity prices vary widely across states, driven by differences in fuel mix, regulatory environment, and infrastructure costs. States with abundant hydropower (e.g., Washington) tend to have the lowest rates, while island states (Hawaii) and those with older infrastructure pay the most.',
		caveats: 'Residential prices only. Commercial and industrial rates follow different patterns. Colors use a yellow-to-red scale where yellow indicates lower prices.',
	});

	function colorInterp(t: number): string {
		return interpolateYlOrRd(t);
	}

	// Market structure map (state name → ISO/RTO)
	const marketMap = $derived(new Map<string, string>(
		data.marketStructure.map((d: any) => [d.state, d.market])
	));

	// Scatter: Prices vs Renewable Share by state
	const priceVsMixData = $derived((() => {
		const priceMap = new Map<string, number>();
		for (const d of data.byState) {
			if (d.year === latestYear && d.sector === 'Residential') {
				priceMap.set(d.state, d.price);
			}
		}
		const renewMap = new Map<string, number>();
		for (const d of data.renewableShare) {
			renewMap.set(d.state, d.renewable_share);
		}
		return [...priceMap.entries()]
			.filter(([state]) => renewMap.has(state))
			.map(([state, price]) => ({
				x: renewMap.get(state)!,
				y: price,
				label: state,
				group: marketMap.get(state) ?? 'Non-ISO',
			}));
	})());

	const scatterMeta: ChartMeta = $derived({
		title: `Electricity Price vs Renewable Share by State (${latestYear})`,
		subtitle: 'Each dot is a state',
		source: 'US Energy Information Administration',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Is there a relationship between renewable energy adoption and electricity prices? This scatter plot shows each state\'s residential electricity price against its renewable generation share. The relationship is complex — states with cheap hydro tend to have both high renewables and low prices, while other factors like grid infrastructure and regulation also play major roles.',
		caveats: 'Correlation does not imply causation. States with high renewable shares include those with abundant hydropower (historically cheap) and those with newer wind/solar capacity (varying cost impact). Residential prices reflect many factors beyond generation mix.',
	});

	// Household electricity bills series
	const billsSeries: DataSeries[] = $derived([
		{
			name: 'Nominal',
			color: '#e86c3a',
			values: data.bills
				.map((d: any) => ({ date: d.year, value: d.nominal_bill }))
				.sort((a: any, b: any) => a.date - b.date),
		},
		{
			name: 'Real (2024$)',
			color: '#2166ac',
			values: data.bills
				.filter((d: any) => d.real_bill != null)
				.map((d: any) => ({ date: d.year, value: d.real_bill }))
				.sort((a: any, b: any) => a.date - b.date),
		},
	]);

	const timeFilteredBills = $derived(
		billsSeries.map((s) => ({
			...s,
			values: s.values.filter((v) => v.date >= startYear && v.date <= endYear),
		}))
	);

	const billsMeta: ChartMeta = {
		title: 'Average Monthly Household Electricity Bill',
		subtitle: 'Dollars per month',
		source: 'US Energy Information Administration + CPI-U',
		sourceUrl: 'https://www.eia.gov/electricity/data.php',
		unit: '$',
		lastUpdated: new Date().toISOString().split('T')[0],
		description: 'Electricity bills have risen in nominal terms but the increase is more modest after adjusting for inflation. The average US household consumes about 900 kWh per month.',
		caveats: 'Bills estimated as average residential price \u00d7 900 kWh/month. Real values adjusted to 2024 dollars using CPI-U.',
	};
</script>

<svelte:head>
	<title>Prices & Bills — US Energy Data</title>
</svelte:head>

<div>
	<!-- Header -->
	<div class="flex items-baseline gap-3 pb-3 border-b border-border">
		<h1 class="text-base font-bold font-display tracking-tight text-text">Prices & Bills</h1>
		<span class="text-sm text-text-secondary">What does your electricity actually cost?</span>
	</div>

	<!-- Sticky control bar -->
	<div class="sticky top-12 z-20 -mx-4 md:-mx-6 lg:-mx-8 bg-surface-card/80 backdrop-blur-xl border-b border-border px-4 md:px-6 lg:px-8 py-2">
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
			<span class="kf-value" style="color: #5B8DEF">{resPrice.toFixed(1)}&cent;</span>
			<span class="kf-label">avg residential</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #5B8DEF">{indPrice.toFixed(1)}&cent;</span>
			<span class="kf-label">avg industrial</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #5B8DEF">{sectorGap}%</span>
			<span class="kf-label">sector gap</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #5B8DEF">{latestYear}</span>
			<span class="kf-label">latest year</span>
		</div>
	</div>

	<!-- Chart grid -->
	<div class="grid gap-3 lg:grid-cols-2 mt-3">
		<!-- Price trends (full-width hero) -->
		<section class="lg:col-span-2">
			<ChartWrapper meta={lineMeta} hero data={timeFilteredSeries.flatMap((s) => s.values.map((v) => ({ series: s.name, year: v.date, price: v.value })))}>
				<LineChart
					series={timeFilteredSeries}
					xLabel="Year"
					yLabel="cents/kWh"
					yFormat={format(',.1f')}
					unit="cents/kWh"
					annotations={priceAnnotations}
				/>
			</ChartWrapper>
		</section>

		<!-- Insight (full-width) -->
		<div class="lg:col-span-2 insight-card">
			<div class="flex items-start gap-4">
				<div class="flex-shrink-0">
					<span class="text-xl font-bold text-accent" style="font-family: var(--font-mono)">50%</span>
					<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">price gap</span>
				</div>
				<p class="text-sm leading-relaxed text-text-secondary">
					Residential customers pay roughly 50% more per kWh than industrial users — a gap that has widened over the past decade.
				</p>
			</div>
		</div>

		<!-- State map (full-width) -->
		<section class="lg:col-span-2">
			<ChartWrapper meta={mapMeta} data={mapData.map((d: any) => ({ state: d.state, price: d.value }))}>
				<ChoroplethMap
					data={mapData}
					topology={data.topology}
					colorInterpolator={colorInterp}
					valueFormat={format(',.1f')}
					unit="cents/kWh"
				/>
			</ChartWrapper>
		</section>

		<!-- Scatter (side-by-side with bills) -->
		<section>
			<ChartWrapper meta={scatterMeta} data={priceVsMixData.map((d) => ({ state: d.label, renewable_share: d.x, price: d.y }))}>
				<Scatter
					data={priceVsMixData}
					xLabel="Renewable share (%)"
					yLabel="Residential price (cents/kWh)"
					xFormat={format(',.0f')}
					yFormat={format(',.1f')}
					unit="cents/kWh"
				/>
			</ChartWrapper>
		</section>

		<!-- Bills -->
		<section>
			<ChartWrapper meta={billsMeta} data={timeFilteredBills.flatMap((s) => s.values.map((v) => ({ year: v.date, [s.name === 'Nominal' ? 'nominal_bill' : 'real_bill']: v.value })))}>
				<LineChart
					series={timeFilteredBills}
					xLabel="Year"
					yLabel="$/month"
					yFormat={format('$,.0f')}
					unit="$"
				/>
			</ChartWrapper>
		</section>
	</div>

	<!-- Cross-link -->
	<p class="mt-3 text-sm">
		<a href="/generation" class="font-medium text-accent/80 hover:text-accent transition-colors no-underline">See how these states generate their electricity &rarr;</a>
	</p>
</div>
