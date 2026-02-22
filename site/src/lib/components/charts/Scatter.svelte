<script lang="ts">
	import { scaleLinear, scaleOrdinal } from 'd3-scale';
	import { extent } from 'd3-array';
	import { format } from 'd3-format';
	import type { Margin, TooltipData } from '$types/chart';
	import { CHART_COLORS } from '$utils/colors';
	import Tooltip from './Tooltip.svelte';
	import { getContext } from 'svelte';
	import type { Readable } from 'svelte/store';

	interface ScatterPoint {
		x: number;
		y: number;
		label: string;
		group?: string;
	}

	interface Props {
		data: ScatterPoint[];
		width?: number;
		height?: number;
		margin?: Margin;
		xLabel?: string;
		yLabel?: string;
		xFormat?: (v: number) => string;
		yFormat?: (v: number) => string;
		unit?: string;
	}

	let {
		data,
		width: propWidth = 800,
		height = 500,
		margin = { top: 20, right: 20, bottom: 50, left: 70 },
		xLabel = '',
		yLabel = '',
		xFormat = format(',.0f'),
		yFormat = format(',.0f'),
		unit = '',
	}: Props = $props();

	const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
	const width = $derived(chartWidthCtx ? $chartWidthCtx : propWidth);

	let tooltip: TooltipData | null = $state(null);
	let hoveredIndex: number | null = $state(null);

	const innerWidth = $derived(width - margin.left - margin.right);
	const innerHeight = $derived(height - margin.top - margin.bottom);

	const xDomain = $derived(extent(data, (d) => d.x) as [number, number]);
	const yDomain = $derived(extent(data, (d) => d.y) as [number, number]);

	const xScale = $derived(scaleLinear().domain(xDomain).range([0, innerWidth]).nice());
	const yScale = $derived(scaleLinear().domain(yDomain).range([innerHeight, 0]).nice());

	const groups = $derived([...new Set(data.map((d) => d.group ?? 'default'))]);
	const colorScale = $derived(
		scaleOrdinal<string>().domain(groups).range(CHART_COLORS as unknown as string[])
	);

	const xTicks = $derived(xScale.ticks(6));
	const yTicks = $derived(yScale.ticks(6));

	function handleDotHover(event: PointerEvent, d: ScatterPoint, index: number) {
		hoveredIndex = index;
		tooltip = {
			x: event.clientX,
			y: event.clientY,
			items: [
				{
					label: d.label,
					value: `${xFormat(d.x)} / ${yFormat(d.y)}`,
					color: colorScale(d.group ?? 'default'),
				},
			],
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
		<!-- Grid -->
		{#each yTicks as tick}
			<line x1={0} x2={innerWidth} y1={yScale(tick)} y2={yScale(tick)} stroke="var(--color-border-light)" />
		{/each}
		{#each xTicks as tick}
			<line x1={xScale(tick)} x2={xScale(tick)} y1={0} y2={innerHeight} stroke="var(--color-border-light)" />
		{/each}

		<!-- Points -->
		{#each data as d, i}
			{@const isHovered = hoveredIndex === i}
			{@const pointOpacity = hoveredIndex === null ? 0.75 : isHovered ? 1 : 0.3}
			{@const pointR = isHovered ? 8 : 6}
			<circle
				cx={xScale(d.x)}
				cy={yScale(d.y)}
				r={pointR}
				fill={colorScale(d.group ?? 'default')}
				fill-opacity={pointOpacity}
				stroke="var(--color-surface)"
				stroke-width="2"
				style="transition: r 0.15s ease, opacity 0.15s ease;"
				onpointermove={(e) => handleDotHover(e, d, i)}
				onpointerleave={handlePointerLeave}
			/>
		{/each}

		<!-- Hover label -->
		{#if hoveredIndex !== null}
			{@const hd = data[hoveredIndex]}
			{@const labelX = xScale(hd.x)}
			{@const labelY = yScale(hd.y) - 14}
			{@const labelText = hd.label}
			<rect
				x={labelX - labelText.length * 3.3 - 4}
				y={labelY - 10}
				width={labelText.length * 6.6 + 8}
				height={16}
				rx="3"
				fill="var(--color-surface-card)"
				fill-opacity="0.9"
				stroke="var(--color-border)"
				stroke-width="0.5"
			/>
			<text
				x={labelX}
				y={labelY}
				text-anchor="middle"
				dominant-baseline="middle"
				font-size="11"
				fill="var(--color-text)"
				font-weight="500"
				pointer-events="none"
			>
				{labelText}
			</text>
		{/if}

		<!-- X axis -->
		<g transform="translate(0, {innerHeight})">
			<line x1={0} x2={innerWidth} stroke="var(--color-border)" />
			{#each xTicks as tick}
				<text x={xScale(tick)} y={20} text-anchor="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
					{xFormat(tick)}
				</text>
			{/each}
			{#if xLabel}
				<text x={innerWidth / 2} y={40} text-anchor="middle" fill="var(--color-text-muted)" font-size="12">
					{xLabel}
				</text>
			{/if}
		</g>

		<!-- Y axis -->
		{#each yTicks as tick}
			<text x={-8} y={yScale(tick)} text-anchor="end" dominant-baseline="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
				{yFormat(tick)}
			</text>
		{/each}
		{#if yLabel}
			<text
				x={-margin.left + 14}
				y={innerHeight / 2}
				text-anchor="middle"
				dominant-baseline="hanging"
				fill="var(--color-text-muted)"
				font-size="12"
				transform="rotate(-90, {-margin.left + 14}, {innerHeight / 2})"
			>
				{yLabel}
			</text>
		{/if}
	</g>
</svg>

<!-- Legend -->
{#if groups.length > 1}
	<div class="mt-2 flex flex-wrap gap-4 px-2 text-sm">
		{#each groups as group}
			<div class="flex items-center gap-1.5">
				<span class="inline-block h-2.5 w-2.5 rounded-full" style="background: {colorScale(group)};"></span>
				<span class="text-text-secondary">{group}</span>
			</div>
		{/each}
	</div>
{/if}

<Tooltip data={tooltip} {unit} />
