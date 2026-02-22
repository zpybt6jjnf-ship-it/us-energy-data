<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import { format } from 'd3-format';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	const saidiAnnotations = [
		{ date: 2020, label: 'COVID-19' },
	];

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

	// Key figures
	const kfLatestSaidi = $derived(data.national.length > 0 ? data.national[data.national.length - 1].saidi : 0);
	const kfLatestYear = $derived(data.national.length > 0 ? data.national[data.national.length - 1].year : 0);
	const kfNumStates = $derived(data.byState.length);
</script>

<svelte:head>
	<title>Reliability & Outages — US Energy Data</title>
</svelte:head>

<div>
	<header>
		<h1 class="text-3xl font-bold tracking-tight text-text" style="font-family: var(--font-display)">Reliability & Outages</h1>
		<div class="mt-2 h-1 w-16 rounded-full" style="background: #984ea3"></div>
		<p class="mt-3 max-w-3xl text-lg leading-relaxed text-text-secondary" style="font-family: var(--font-display)">
			How often does the power go out — and for how long?
		</p>
	</header>

	<!-- Key Figures -->
	<div class="key-figures">
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">~{Math.round(kfLatestSaidi)}</span>
			<span class="kf-label">min avg outage/yr</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">{kfNumStates}</span>
			<span class="kf-label">states tracked</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">{kfLatestYear}</span>
			<span class="kf-label">latest year</span>
		</div>
		<div class="key-figure">
			<span class="sample-badge">Sample Data</span>
			<span class="kf-label">Phase 2 planned</span>
		</div>
	</div>

	<!-- Sample data banner -->
	<div class="rounded-lg border border-amber-200/60 bg-amber-50/60 px-5 py-3 mt-2 mb-6">
		<p class="text-xs font-medium text-amber-800">
			This page uses representative sample data. Real EIA-861 reliability metrics are planned for Phase 2.
		</p>
	</div>

	<!-- Chart 1: National SAIDI trend (hero chart) -->
	<section>
		<ChartWrapper meta={lineMeta} hero category="Reliability" categoryColor="#984ea3" data={data.national}>
			<LineChart
				series={saidiSeries}
				xLabel="Year"
				yLabel="Minutes per customer"
				yFormat={format(',.0f')}
				unit="min"
				annotations={saidiAnnotations}
			/>
		</ChartWrapper>
	</section>

	<!-- Insight -->
	<div class="insight-card my-8">
		<div class="flex items-start gap-4">
			<div class="flex-shrink-0">
				<span class="text-3xl font-bold text-accent" style="font-family: var(--font-mono)">~2hr</span>
				<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">avg outage</span>
			</div>
			<p class="text-base leading-relaxed text-text-secondary">
				The average US customer experiences about 2 hours of power outages per year — but major weather events can push some states well above that.
			</p>
		</div>
	</div>

	<!-- Cross-link -->
	<p class="mt-8 text-sm">
		<a href="/prices" class="text-accent/80 hover:text-accent transition-colors no-underline">Does reliability affect what you pay? Explore electricity prices &rarr;</a>
	</p>

	<div class="section-divider"></div>

	<!-- Chart 2: SAIDI vs SAIFI scatter -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl mt-16">
		<ChartWrapper meta={scatterMeta} category="Reliability" categoryColor="#984ea3" data={data.byState}>
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
