<script lang="ts">
	import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
	import { format } from 'd3-format';
	import type { Margin, TooltipData } from '$types/chart';
	import { CHART_COLORS } from '$utils/colors';
	import Tooltip from './Tooltip.svelte';

	interface BarData {
		label: string;
		value: number;
		color?: string;
	}

	interface Props {
		data: BarData[];
		width?: number;
		height?: number;
		margin?: Margin;
		horizontal?: boolean;
		xLabel?: string;
		yLabel?: string;
		yFormat?: (v: number) => string;
		unit?: string;
	}

	let {
		data,
		width = 800,
		height = 400,
		margin = { top: 20, right: 20, bottom: 60, left: 60 },
		horizontal = false,
		xLabel = '',
		yLabel = '',
		yFormat = format(',.0f'),
		unit = '',
	}: Props = $props();

	let tooltip: TooltipData | null = $state(null);
	let hoveredIndex: number | null = $state(null);

	const innerWidth = $derived(width - margin.left - margin.right);
	const innerHeight = $derived(height - margin.top - margin.bottom);

	const labels = $derived(data.map((d) => d.label));
	const maxValue = $derived(Math.max(...data.map((d) => d.value)) * 1.1);

	const bandScale = $derived(
		scaleBand().domain(labels).range([0, horizontal ? innerHeight : innerWidth]).padding(0.2)
	);

	const valueScale = $derived(
		scaleLinear()
			.domain([0, maxValue])
			.range(horizontal ? [0, innerWidth] : [innerHeight, 0])
			.nice()
	);

	const colorScale = $derived(
		scaleOrdinal<string>().domain(labels).range(
			data.map((d, i) => d.color ?? CHART_COLORS[i % CHART_COLORS.length])
		)
	);

	// Detect if bars use multiple distinct colors (for legend)
	const uniqueColors = $derived([...new Set(data.map((d, i) => d.color ?? CHART_COLORS[i % CHART_COLORS.length]))]);
	const hasMultipleColors = $derived(uniqueColors.length > 1);

	const valueTicks = $derived(valueScale.ticks(6));

	function handleBarHover(event: PointerEvent, d: BarData, index: number) {
		hoveredIndex = index;
		tooltip = {
			x: event.clientX,
			y: event.clientY,
			items: [{ label: d.label, value: yFormat(d.value), color: colorScale(d.label) }],
		};
	}

	function handlePointerLeave() {
		hoveredIndex = null;
		tooltip = null;
	}
</script>

<svg
	class="chart"
	viewBox="0 0 {width} {height}"
	style="max-width: {width}px; width: 100%; height: auto;"
>
	<g transform="translate({margin.left}, {margin.top})">
		<!-- Grid lines -->
		{#each valueTicks as tick}
			{#if horizontal}
				<line
					x1={valueScale(tick)}
					x2={valueScale(tick)}
					y1={0}
					y2={innerHeight}
					stroke="#efecea"
				/>
			{:else}
				<line
					x1={0}
					x2={innerWidth}
					y1={valueScale(tick)}
					y2={valueScale(tick)}
					stroke="#efecea"
				/>
			{/if}
		{/each}

		<!-- Bars -->
		{#each data as d, i}
			{@const bandPos = bandScale(d.label) ?? 0}
			{@const bandWidth = bandScale.bandwidth()}
			{@const barOpacity = hoveredIndex === null ? 1 : hoveredIndex === i ? 1 : 0.4}
			{#if horizontal}
				<rect
					x={0}
					y={bandPos}
					width={valueScale(d.value)}
					height={bandWidth}
					fill={colorScale(d.label)}
					rx="3"
					shape-rendering="crispEdges"
					opacity={barOpacity}
					style="transition: opacity 0.2s ease;"
					onpointermove={(e) => handleBarHover(e, d, i)}
					onpointerleave={handlePointerLeave}
				/>
			{:else}
				<rect
					x={bandPos}
					y={valueScale(d.value)}
					width={bandWidth}
					height={innerHeight - valueScale(d.value)}
					fill={colorScale(d.label)}
					rx="3"
					shape-rendering="crispEdges"
					opacity={barOpacity}
					style="transition: opacity 0.2s ease;"
					onpointermove={(e) => handleBarHover(e, d, i)}
					onpointerleave={handlePointerLeave}
				/>
			{/if}
		{/each}

		<!-- Axes -->
		{#if horizontal}
			<!-- Value axis (bottom) -->
			<g transform="translate(0, {innerHeight})">
				<line x1={0} x2={innerWidth} stroke="#e5e2dc" />
				{#each valueTicks as tick}
					<text x={valueScale(tick)} y={20} text-anchor="middle" fill="#5a6270" font-size="13">
						{yFormat(tick)}
					</text>
				{/each}
			</g>
			<!-- Category axis (left) -->
			{#each data as d}
				<text
					x={-8}
					y={(bandScale(d.label) ?? 0) + bandScale.bandwidth() / 2}
					text-anchor="end"
					dominant-baseline="middle"
					fill="#5a6270"
					font-size="13"
				>
					{d.label}
				</text>
			{/each}
		{:else}
			<!-- Value axis (left) -->
			{#each valueTicks as tick}
				<text x={-8} y={valueScale(tick)} text-anchor="end" dominant-baseline="middle" fill="#5a6270" font-size="13">
					{yFormat(tick)}
				</text>
			{/each}
			<!-- Category axis (bottom) -->
			<g transform="translate(0, {innerHeight})">
				<line x1={0} x2={innerWidth} stroke="#e5e2dc" />
				{#each data as d}
					<text
						x={(bandScale(d.label) ?? 0) + bandScale.bandwidth() / 2}
						y={20}
						text-anchor="middle"
						fill="#5a6270"
						font-size="13"
						class="truncate"
					>
						{d.label.length > 12 ? d.label.slice(0, 11) + '…' : d.label}
					</text>
				{/each}
			</g>
		{/if}

	</g>
</svg>

<!-- Legend for multi-colored bars -->
{#if hasMultipleColors}
	<div class="mt-2 flex flex-wrap gap-4 px-2 text-sm">
		{#each data as d, i}
			<div class="flex items-center gap-1.5">
				<span class="inline-block h-2.5 w-2.5 rounded" style="background: {colorScale(d.label)};"></span>
				<span class="text-gray-600">{d.label}</span>
			</div>
		{/each}
	</div>
{/if}

<Tooltip data={tooltip} {unit} />
