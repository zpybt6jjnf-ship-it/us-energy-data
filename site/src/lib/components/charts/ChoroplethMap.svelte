<script lang="ts">
	import { geoAlbersUsa, geoPath } from 'd3-geo';
	import { scaleSequential } from 'd3-scale';
	import { interpolateRgb } from 'd3-interpolate';
	import { format } from 'd3-format';
	import type { Margin, TooltipData } from '$types/chart';
	import Tooltip from './Tooltip.svelte';
	import { FIPS_TO_ABBR } from '$lib/utils/states';
	import { getContext } from 'svelte';
	import type { Readable } from 'svelte/store';

	interface MapData {
		state: string;
		fips: string;
		value: number;
	}

	interface Props {
		data: MapData[];
		topology: any;
		width?: number;
		height?: number;
		colorInterpolator?: (t: number) => string;
		valueFormat?: (v: number) => string;
		unit?: string;
	}

	/** Custom brand-aligned interpolator: light cream → deep blue */
	const brandInterpolator = interpolateRgb('#fef9ef', '#0f2b44');

	let {
		data,
		topology,
		width: propWidth = 960,
		height: propHeight = 600,
		colorInterpolator = brandInterpolator,
		valueFormat = format(',.1f'),
		unit = '',
	}: Props = $props();

	const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
	const width = $derived(chartWidthCtx ? $chartWidthCtx : propWidth);
	const height = $derived(Math.round(width * 0.625));

	let tooltip: TooltipData | null = $state(null);
	let hoveredFips: string | null = $state(null);

	/** Reserve space above the map for the legend */
	const legendAreaHeight = 50;

	const projection = $derived(
		geoAlbersUsa().fitSize([width, height - legendAreaHeight], topology)
	);

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
	const legendWidth = 300;
	const legendHeight = 12;
	const noDataColor = 'var(--color-border)';

	const legendX = $derived((width - legendWidth) / 2);

	/** FIPS codes of very small states — skip labels to avoid clutter */
	const smallStateFips = new Set(['11', '44', '09', '34', '10', '24', '25', '33', '50']);

	/**
	 * Determine label fill color based on the normalized position in the domain.
	 * Values in the upper 50% of the range get white text; lower 50% get dark text.
	 */
	function labelFill(fips: string): string {
		const val = valueMap.get(fips);
		if (!val) return 'var(--color-text)';
		const range = domain[1] - domain[0];
		if (range === 0) return 'var(--color-text)';
		const t = (val.value - domain[0]) / range;
		return t > 0.5 ? '#ffffff' : 'var(--color-text)';
	}

	function handleStateHover(event: PointerEvent, fips: string) {
		hoveredFips = fips;
		const d = valueMap.get(fips);
		if (!d) return;
		tooltip = {
			x: event.clientX,
			y: event.clientY,
			items: [{ label: d.state, value: valueFormat(d.value), color: colorScale(d.value) }],
		};
	}

	function handlePointerLeave() {
		hoveredFips = null;
		tooltip = null;
	}
</script>

<svg
	class="chart choropleth-map"
	viewBox="0 0 {width} {height}"
	style="max-width: {width}px; width: 100%; height: auto;"
	role="img"
	aria-label="Choropleth map of the United States"
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
	<g transform="translate(0, {legendAreaHeight})">
		{#each topology.features as feature}
			{@const d = pathGenerator(feature)}
			{@const fips = feature.id ?? feature.properties?.STATEFP}
			{@const val = valueMap.get(fips)}
			{@const isHovered = hoveredFips === fips}
			{#if d}
				<path
					{d}
					fill={val ? colorScale(val.value) : noDataColor}
					stroke={isHovered ? 'var(--color-text)' : 'var(--color-surface)'}
					stroke-width={isHovered ? 2 : 1}
					class="state-path"
					onpointermove={(e) => handleStateHover(e, fips)}
					onpointerleave={handlePointerLeave}
				/>
			{/if}
		{/each}

		<!-- State abbreviation labels -->
		{#each topology.features as feature}
			{@const fips = feature.id ?? feature.properties?.STATEFP}
			{@const abbr = FIPS_TO_ABBR[fips]}
			{@const centroid = pathGenerator.centroid(feature)}
			{#if abbr && centroid && !isNaN(centroid[0]) && !isNaN(centroid[1]) && !smallStateFips.has(fips)}
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

<Tooltip data={tooltip} {unit} />

<style>
	.state-path {
		transition: stroke 0.15s ease, stroke-width 0.15s ease;
		cursor: pointer;
	}
</style>
