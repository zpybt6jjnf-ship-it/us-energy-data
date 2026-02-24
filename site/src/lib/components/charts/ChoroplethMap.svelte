<script lang="ts">
	import { geoAlbersUsa, geoPath } from 'd3-geo';
	import { scaleSequential } from 'd3-scale';
	import { interpolateRgb } from 'd3-interpolate';
	import { format } from 'd3-format';
	import type { Margin, TooltipData } from '$types/chart';
	import type { FeatureCollection, Geometry, GeoJsonProperties } from 'geojson';
	import Tooltip from './Tooltip.svelte';
	import { MAP_DEFAULT_RANGE, MAP_LABEL_COLORS } from '$utils/colors';
	import { FIPS_TO_ABBR } from '$lib/utils/states';
	import { getContext } from 'svelte';
	import type { Readable, Writable } from 'svelte/store';

	interface MapData {
		state: string;
		fips: string;
		value: number;
	}

	interface Props {
		data: MapData[];
		topology: FeatureCollection<Geometry, GeoJsonProperties & { STATEFP?: string }>;
		width?: number;
		height?: number;
		colorInterpolator?: (t: number) => string;
		valueFormat?: (v: number) => string;
		unit?: string;
		onStateClick?: (stateAbbr: string) => void;
	}

	/** Custom brand-aligned interpolator: cream → blue */
	const brandInterpolator = interpolateRgb(MAP_DEFAULT_RANGE[0], MAP_DEFAULT_RANGE[1]);

	let {
		data,
		topology,
		width: propWidth = 960,
		height: propHeight = 600,
		colorInterpolator = brandInterpolator,
		valueFormat = format(',.1f'),
		unit = '',
		onStateClick,
	}: Props = $props();

	const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
	const width = $derived(chartWidthCtx ? ($chartWidthCtx ?? propWidth) : propWidth);
	const height = $derived(Math.round(width * 0.625));

	const chartVisibleCtx = getContext<Writable<boolean> | undefined>('chartVisible');
	const chartVisible = $derived(chartVisibleCtx ? $chartVisibleCtx : true);

	const chartTitleCtx = getContext<Readable<string> | undefined>('chartTitle');
	const chartTitle = $derived(chartTitleCtx ? $chartTitleCtx : '');

	let tooltip: TooltipData | null = $state(null);
	let hoveredFips: string | null = $state(null);

	/** Reserve space above the map for the legend */
	const legendAreaHeight = 50;

	/** Memoize projection — only recompute when dimensions change */
	let prevDims = $state({ w: 0, h: 0 });
	let cachedProjection = $state(geoAlbersUsa());
	const projection = $derived.by(() => {
		const h = height - legendAreaHeight;
		if (prevDims.w === width && prevDims.h === h) return cachedProjection;
		prevDims = { w: width, h };
		cachedProjection = geoAlbersUsa().fitSize([width, h], topology);
		return cachedProjection;
	});

	const pathGenerator = $derived(geoPath(projection));

	const valueMap = $derived(
		new Map(data.map((d) => [d.fips, d]))
	);

	const domain = $derived([
		Math.min(...data.map((d) => d.value)),
		Math.max(...data.map((d) => d.value)),
	] as [number, number]);

	const colorScale = $derived(
		scaleSequential(colorInterpolator).domain(domain)
	);

	const legendSteps = 8;
	const legendWidth = $derived(Math.min(300, width - 80));
	const legendHeight = 12;
	const noDataColor = 'var(--color-border)';

	const legendX = $derived((width - legendWidth) / 2);

	/** FIPS codes of very small states — skip labels to avoid clutter */
	const smallStateFips = new Set(['11', '44', '09', '34', '10', '24', '25', '33', '50']);

	/** Minimum vertical spacing (px) between labels to avoid overlap */
	const labelMinSpacing = 13;

	/**
	 * Collision-free label set: compute centroids, sort by y, then greedily
	 * skip labels whose vertical position is too close to the previous visible one.
	 */
	const visibleLabelFips = $derived.by(() => {
		const candidates: { fips: string; x: number; y: number }[] = [];
		for (const feature of topology.features) {
			const fips = (feature.id ?? feature.properties?.STATEFP) as string;
			const abbr = FIPS_TO_ABBR[fips];
			if (!abbr || smallStateFips.has(fips)) continue;
			const centroid = pathGenerator.centroid(feature);
			if (!centroid || isNaN(centroid[0]) || isNaN(centroid[1])) continue;
			candidates.push({ fips, x: centroid[0], y: centroid[1] });
		}
		// Sort by y position (top to bottom)
		candidates.sort((a, b) => a.y - b.y);

		const visible = new Set<string>();
		let lastY = -Infinity;
		for (const c of candidates) {
			if (c.y - lastY >= labelMinSpacing) {
				visible.add(c.fips);
				lastY = c.y;
			}
		}
		return visible;
	});

	/**
	 * Determine label fill color based on the normalized position in the domain.
	 * High values (bright amber) get dark text; low values (dark base) get light text.
	 */
	function labelFill(fips: string): string {
		const val = valueMap.get(fips);
		if (!val) return MAP_LABEL_COLORS.dark;
		const range = domain[1] - domain[0];
		if (range === 0) return MAP_LABEL_COLORS.dark;
		const t = (val.value - domain[0]) / range;
		return t > 0.5 ? MAP_LABEL_COLORS.light : MAP_LABEL_COLORS.dark;
	}

	function handleStateHover(event: PointerEvent, fips: string) {
		hoveredFips = fips;
		const d = valueMap.get(fips);
		if (!d) return;
		tooltip = {
			x: event.clientX,
			y: event.clientY,
			header: d.state,
			subtitle: unit || undefined,
			items: [{ label: valueFormat(d.value), value: unit || '', color: colorScale(d.value) }],
		};
	}

	function handlePointerLeave() {
		hoveredFips = null;
		tooltip = null;
	}
</script>

{#if data.length > 0}
<svg
	class="chart choropleth-map"
	viewBox="0 0 {width} {height}"
	style="max-width: {width}px; width: 100%; height: auto;"
	role="img"
	aria-label={chartTitle || 'Choropleth map of the United States'}
>
	<!-- Color legend — centered above the map -->
	<g transform="translate({legendX}, 4)">
		<!-- Unit label above the gradient -->
		{#if unit}
			<text
				x={legendWidth / 2}
				y={0}
				fill="var(--color-text-secondary)"
				font-size="11"
				font-family="var(--font-sans)"
				text-anchor="middle"
				dominant-baseline="hanging"
			>{unit}</text>
		{/if}

		<!-- Gradient bar -->
		{#each Array.from({ length: legendSteps }, (_, i) => i) as i}
			{@const val = domain[0] + (i / (legendSteps - 1)) * (domain[1] - domain[0])}
			<rect
				x={i * (legendWidth / legendSteps)}
				y={unit ? 16 : 0}
				width={legendWidth / legendSteps + 0.5}
				height={legendHeight}
				fill={colorScale(val)}
			/>
		{/each}

		<!-- Min / max labels -->
		<text
			x={0}
			y={unit ? 16 + legendHeight + 14 : legendHeight + 14}
			fill="var(--color-text-secondary)"
			font-size="12"
			font-family="var(--font-sans)"
			text-anchor="start"
		>{valueFormat(domain[0])}</text>
		<text
			x={legendWidth}
			y={unit ? 16 + legendHeight + 14 : legendHeight + 14}
			fill="var(--color-text-secondary)"
			font-size="12"
			font-family="var(--font-sans)"
			text-anchor="end"
		>{valueFormat(domain[1])}</text>

		<!-- No data swatch -->
		<rect
			x={legendWidth + 16}
			y={unit ? 16 : 0}
			width={legendHeight}
			height={legendHeight}
			fill={noDataColor}
			rx="1"
		/>
		<text
			x={legendWidth + 16 + legendHeight + 6}
			y={unit ? 16 + legendHeight / 2 : legendHeight / 2}
			fill="var(--color-text-secondary)"
			font-size="11"
			font-family="var(--font-sans)"
			dominant-baseline="central"
		>No data</text>
	</g>

	<!-- State paths — offset down to make room for legend -->
	<g transform="translate(0, {legendAreaHeight})" opacity={chartVisible ? 1 : 0} style="transition: opacity 0.6s ease;">
		{#each topology.features as feature}
			{@const d = pathGenerator(feature)}
			{@const fips = String(feature.id ?? feature.properties?.STATEFP ?? '')}
			{@const val = valueMap.get(fips)}
			{@const isHovered = hoveredFips === fips}
			{#if d}
				<!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
				<path
					{d}
					fill={val ? colorScale(val.value) : noDataColor}
					stroke={isHovered ? 'var(--color-text)' : 'var(--color-surface)'}
					stroke-width={isHovered ? 2 : 1}
					class="state-path"
					role={onStateClick ? 'button' : undefined}
					tabindex={onStateClick ? 0 : undefined}
					onpointermove={(e) => handleStateHover(e, fips)}
					onpointerleave={handlePointerLeave}
					onclick={() => {
						const abbr = FIPS_TO_ABBR[fips];
						if (abbr && onStateClick) onStateClick(abbr);
					}}
					onkeydown={(e) => {
						if (e.key === 'Enter' || e.key === ' ') {
							e.preventDefault();
							const abbr = FIPS_TO_ABBR[fips];
							if (abbr && onStateClick) onStateClick(abbr);
						}
					}}
				/>
			{/if}
		{/each}

		<!-- State abbreviation labels (collision-filtered) -->
		{#each topology.features as feature}
			{@const fips = String(feature.id ?? feature.properties?.STATEFP ?? '')}
			{@const abbr = FIPS_TO_ABBR[fips]}
			{@const centroid = pathGenerator.centroid(feature)}
			{#if abbr && centroid && !isNaN(centroid[0]) && !isNaN(centroid[1]) && visibleLabelFips.has(fips)}
				<text
					x={centroid[0]}
					y={centroid[1]}
					fill={labelFill(fips)}
					font-size="9"
					font-weight="600"
					font-family="var(--font-sans)"
					text-anchor="middle"
					dominant-baseline="central"
					pointer-events="none"
				>{abbr}</text>
			{/if}
		{/each}
	</g>
</svg>

<Tooltip data={tooltip} />
{:else}
<p class="text-sm text-text-muted py-12 text-center">No data available</p>
{/if}

<style>
	.state-path {
		transition: stroke 0.15s ease, stroke-width 0.15s ease;
		cursor: pointer;
	}
</style>
