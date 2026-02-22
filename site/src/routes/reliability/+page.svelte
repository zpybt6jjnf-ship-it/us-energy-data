<script lang="ts">
	import LineChart from '$components/charts/LineChart.svelte';
	import Scatter from '$components/charts/Scatter.svelte';
	import ChoroplethMap from '$components/charts/ChoroplethMap.svelte';
	import ChartWrapper from '$components/charts/ChartWrapper.svelte';
	import Dropdown from '$components/ui/Dropdown.svelte';
	import StateSelect from '$components/ui/StateSelect.svelte';
	import { chartConfig, updateConfig } from '$stores/chartConfig';
	import { stateFromAbbr } from '$utils/states';
	import { CHART_COLORS } from '$utils/colors';
	import { format } from 'd3-format';
	import { interpolateYlOrRd } from 'd3-scale-chromatic';
	import type { DataSeries, ChartMeta } from '$types/chart';

	let { data } = $props();

	// --- Controls ---
	const medOptions = [
		{ value: 'with_med', label: 'With Major Event Days' },
		{ value: 'without_med', label: 'Without Major Event Days' },
	];

	const activeMed = $derived(
		$chartConfig.med === 'without_med' ? 'without_med' : 'with_med'
	);

	// --- Chart 1: National SAIDI trend ---
	const saidiField = $derived(activeMed === 'without_med' ? 'saidi_no_med' : 'saidi');
	const saifiField = $derived(activeMed === 'without_med' ? 'saifi_no_med' : 'saifi');

	const saidiSeries: DataSeries[] = $derived([
		{
			name: 'SAIDI (avg. interruption minutes)',
			values: data.national.map((d: any) => ({
				date: d.year,
				value: d[saidiField],
			})),
		},
	]);

	const saidiAnnotations = [
		{ date: 2017, label: 'Harvey/Irma' },
		{ date: 2020, label: 'Derecho' },
		{ date: 2021, label: 'Winter Storm Uri' },
		{ date: 2024, label: 'Helene/Milton' },
	];

	const lineMeta: ChartMeta = $derived({
		title: 'Average Power Outage Duration Over Time',
		subtitle: activeMed === 'without_med'
			? 'SAIDI excluding major event days, US customer-weighted average'
			: 'System Average Interruption Duration Index (SAIDI), US customer-weighted average',
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: 'minutes/customer/year',
		lastUpdated: '2024',
		description: 'SAIDI measures the average total duration of power interruptions per customer per year, weighted by number of customers served. Data aggregated from ~950 utility reports filed annually with the EIA.',
		caveats: activeMed === 'with_med'
			? 'Including major event days (hurricanes, ice storms, etc.) causes large year-to-year variation. Toggle to "Without Major Event Days" for a steadier trend.'
			: 'Excluding major event days removes the impact of catastrophic weather events (hurricanes, ice storms) to show underlying grid reliability trends.',
	});

	// --- State comparison overlay on SAIDI trend ---
	const selectedStates = $derived($chartConfig.states);

	const stateSaidiSeries: DataSeries[] = $derived(
		selectedStates.map((abbr, i) => {
			return {
				name: abbr,
				color: CHART_COLORS[(1 + i) % CHART_COLORS.length],
				values: data.byStateTrend
					.filter((d: any) => d.stateAbbr === abbr && d.saidi != null)
					.map((d: any) => ({ date: d.year, value: d.saidi }))
					.sort((a: any, b: any) => a.date - b.date),
			};
		}).filter((s) => s.values.length > 0)
	);

	const combinedSaidiSeries = $derived([...saidiSeries, ...stateSaidiSeries]);

	// --- Choropleth: SAIDI by state ---
	const mapData = $derived(
		data.byState
			.map((d: any) => ({ state: d.state, fips: d.fips, value: d[saidiField] }))
			.filter((d: { fips: string; value: number | null }) => d.fips && d.value != null)
	);

	const mapMeta: ChartMeta = $derived({
		title: 'Power Outage Duration by State',
		subtitle: `SAIDI by state (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${data.byState[0]?.year || 2024}`,
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: 'minutes/customer/year',
		lastUpdated: String(data.byState[0]?.year || 2024),
		description: 'Customer-weighted average outage duration (SAIDI) for each state. Darker colors indicate longer average outages. Southeastern and Gulf Coast states tend to experience more outage minutes due to hurricane and severe weather exposure.',
		caveats: 'State averages are computed from individual utility reports weighted by customers served. States with few reporting utilities may have less reliable averages.',
	});

	// --- Chart 2: SAIDI vs SAIFI scatter ---
	const saidiVsSaifi = $derived(
		data.byState
			.filter((d: any) => d[saidiField] != null && d[saifiField] != null)
			.map((d: any) => ({
				x: d[saidiField],
				y: d[saifiField],
				label: d.stateAbbr || d.state,
				group: d[saidiField] > 500 ? 'High outage states' : 'Other states',
			}))
	);

	const scatterMeta: ChartMeta = $derived({
		title: 'Outage Duration vs Frequency by State',
		subtitle: `SAIDI vs SAIFI (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${data.byState[0]?.year || 2024}`,
		source: 'EIA-861 Annual Electric Power Industry Report',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: String(data.byState[0]?.year || 2024),
		description: 'Each dot is a US state. States with longer average outage duration (SAIDI) tend to also have more frequent interruptions (SAIFI). Data is customer-weighted from utility reports.',
		caveats: 'Southeastern and Gulf Coast states often appear in the upper right due to hurricane exposure. Some states have few reporting utilities, which can skew averages.',
	});

	// --- Market structure map (state name → ISO/RTO) ---
	const marketMap = $derived(new Map<string, string>(
		data.marketStructure.map((d: any) => [d.state, d.market])
	));

	// --- Chart 3: Reliability vs Prices scatter ---
	const latestYear = $derived(data.byState[0]?.year || 2024);

	const reliabilityVsPrices = $derived((() => {
		// Get residential prices for the latest reliability data year
		const priceMap = new Map<string, number>();
		for (const p of data.pricesByState) {
			if (p.year === latestYear && p.sector === 'Residential') {
				priceMap.set(p.state, p.price);
			}
		}
		// If exact year not found, try the year before
		if (priceMap.size === 0) {
			for (const p of data.pricesByState) {
				if (p.year === latestYear - 1 && p.sector === 'Residential') {
					priceMap.set(p.state, p.price);
				}
			}
		}

		return data.byState
			.filter((d: any) => d[saidiField] != null && priceMap.has(d.state))
			.map((d: any) => ({
				x: d[saidiField],
				y: priceMap.get(d.state)!,
				label: d.stateAbbr || d.state,
				group: marketMap.get(d.state) ?? 'Non-ISO',
			}));
	})());

	const priceScatterMeta: ChartMeta = $derived({
		title: 'Do Unreliable Grids Cost More?',
		subtitle: `SAIDI vs residential electricity price by state (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days), ${latestYear}`,
		source: 'EIA-861 (reliability) + EIA Retail Sales (prices)',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: String(latestYear),
		description: 'Compares each state\'s average outage duration (SAIDI) against its residential electricity price. If poor reliability correlated with higher prices, points would trend upward to the right.',
		caveats: 'Electricity prices are driven by many factors (fuel mix, regulation, geography) beyond grid reliability. This chart shows correlation, not causation.',
	});

	// --- Chart 4: Renewables vs Reliability scatter ---
	const renewVsReliability = $derived((() => {
		const renewMap = new Map<string, number>();
		for (const r of data.renewableShare) {
			renewMap.set(r.state, r.renewable_share);
		}
		return data.byState
			.filter((d: any) => d[saidiField] != null && renewMap.has(d.state))
			.map((d: any) => ({
				x: renewMap.get(d.state)!,
				y: d[saidiField],
				label: d.stateAbbr || d.state,
				group: renewMap.get(d.state)! > 30 ? 'High renewable states' : 'Other states',
			}));
	})());

	const renewScatterMeta: ChartMeta = $derived({
		title: 'Do Renewables Hurt Grid Reliability?',
		subtitle: `Renewable generation share vs SAIDI (${activeMed === 'without_med' ? 'excl.' : 'incl.'} major event days) by state, ${latestYear}`,
		source: 'EIA-861 (reliability) + EIA-923/860 (generation)',
		sourceUrl: 'https://www.eia.gov/electricity/data/eia861/',
		unit: '',
		lastUpdated: String(latestYear),
		description: 'Compares each state\'s renewable electricity share against its average outage duration (SAIDI). If more renewables caused worse reliability, points would trend upward to the right.',
		caveats: 'Renewable share includes hydro, wind, solar, geothermal, and biomass. Reliability depends on many factors beyond generation mix (grid age, weather exposure, vegetation management). This shows correlation, not causation.',
	});

	// --- Key figures ---
	const kfLatest = $derived(data.national.length > 0 ? data.national[data.national.length - 1] : null);
	const kfLatestSaidi = $derived(kfLatest ? kfLatest.saidi : 0);
	const kfLatestSaidiNoMed = $derived(kfLatest ? kfLatest.saidi_no_med : 0);
	const kfLatestYear = $derived(kfLatest ? kfLatest.year : 0);
	const kfNumStates = $derived(data.byState.length);
	const kfNumUtilities = $derived(kfLatest ? kfLatest.utilities : 0);
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
			<span class="kf-value" style="color: #984ea3">~{Math.round(kfLatestSaidi / 60)}hr</span>
			<span class="kf-label">avg outage/yr ({kfLatestYear})</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">{Math.round(kfLatestSaidiNoMed)}</span>
			<span class="kf-label">min excl. major events</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">{kfNumStates}</span>
			<span class="kf-label">states + DC tracked</span>
		</div>
		<div class="key-figure">
			<span class="kf-value" style="color: #984ea3">{format(',')(kfNumUtilities)}</span>
			<span class="kf-label">reporting utilities</span>
		</div>
	</div>

	<!-- Controls -->
	<div class="mt-10 flex flex-wrap items-end gap-4 mb-4">
		<Dropdown
			label="Metric"
			options={medOptions}
			value={activeMed}
			onchange={(v) => updateConfig('med', v)}
		/>
		<StateSelect
			selected={selectedStates}
			onchange={(states) => updateConfig('state', states)}
		/>
	</div>

	<!-- Chart 1: National SAIDI trend (hero chart) -->
	<section>
		<ChartWrapper meta={lineMeta} hero category="Reliability" categoryColor="#984ea3" data={data.national}>
			<LineChart
				series={combinedSaidiSeries}
				xLabel="Year"
				yLabel="Minutes per customer"
				yFormat={format(',.0f')}
				unit="min"
				annotations={activeMed === 'with_med' ? saidiAnnotations : []}
			/>
		</ChartWrapper>
	</section>

	<!-- Insight -->
	<div class="insight-card my-8">
		<div class="flex items-start gap-4">
			<div class="flex-shrink-0">
				<span class="text-3xl font-bold text-accent" style="font-family: var(--font-mono)">~{Math.round(kfLatestSaidi / 60)}hr</span>
				<span class="block text-[10px] uppercase tracking-wider text-text-muted mt-0.5">avg outage ({kfLatestYear})</span>
			</div>
			<p class="text-base leading-relaxed text-text-secondary">
				The average US customer experienced about {Math.round(kfLatestSaidi / 60)} hours of power outages in {kfLatestYear} — but excluding major events (hurricanes, ice storms), the baseline is roughly {Math.round(kfLatestSaidiNoMed)} minutes.
			</p>
		</div>
	</div>

	<!-- Choropleth: SAIDI by state -->
	<section class="mt-8">
		<ChartWrapper meta={mapMeta} category="Reliability" categoryColor="#984ea3" data={mapData}>
			<ChoroplethMap
				data={mapData}
				topology={data.topology}
				colorInterpolator={interpolateYlOrRd}
				valueFormat={format(',.0f')}
				unit="min"
			/>
		</ChartWrapper>
	</section>

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

	<div class="section-divider"></div>

	<!-- Chart 3: Reliability vs Prices scatter -->
	<section class="mt-8">
		<ChartWrapper meta={priceScatterMeta} category="Reliability" categoryColor="#984ea3" data={reliabilityVsPrices}>
			<Scatter
				data={reliabilityVsPrices}
				xLabel="SAIDI (minutes/customer/year)"
				yLabel="Residential price (cents/kWh)"
				xFormat={format(',.0f')}
				yFormat={format('.1f')}
				unit="c/kWh"
			/>
		</ChartWrapper>
	</section>

	<div class="section-divider"></div>

	<!-- Chart 4: Renewables vs Reliability scatter -->
	<section class="-mx-6 bg-surface-alt px-6 py-12 sm:-mx-8 sm:px-8 md:rounded-xl mt-16">
		<ChartWrapper meta={renewScatterMeta} category="Reliability" categoryColor="#984ea3" data={renewVsReliability}>
			<Scatter
				data={renewVsReliability}
				xLabel="Renewable share (%)"
				yLabel="SAIDI (minutes/customer/year)"
				xFormat={format('.0f')}
				yFormat={format(',.0f')}
				unit="min"
			/>
		</ChartWrapper>
	</section>

	<!-- Cross-link -->
	<p class="mt-8 text-sm">
		<a href="/prices" class="text-accent/80 hover:text-accent transition-colors no-underline">Explore electricity prices in more detail &rarr;</a>
	</p>
</div>
