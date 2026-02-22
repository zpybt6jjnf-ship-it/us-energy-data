<script lang="ts">
	import { scaleLinear, scaleOrdinal } from 'd3-scale';
	import { line as d3line, curveMonotoneX } from 'd3-shape';
	import { extent } from 'd3-array';
	import { format } from 'd3-format';
	import type { DataSeries, Margin, TooltipData } from '$types/chart';
	import { CHART_COLORS } from '$utils/colors';
	import Tooltip from './Tooltip.svelte';
	import { getContext } from 'svelte';
	import type { Readable, Writable } from 'svelte/store';

	interface Annotation {
		date: number;
		label: string;
		labelPosition?: 'top' | 'bottom';
	}

	interface Props {
		series: DataSeries[];
		width?: number;
		height?: number;
		margin?: Margin;
		xLabel?: string;
		yLabel?: string;
		yFormat?: (v: number) => string;
		unit?: string;
		annotations?: Annotation[];
	}

	let {
		series,
		width: propWidth = 800,
		height = 400,
		margin = { top: 20, right: 130, bottom: 40, left: 60 },
		xLabel = '',
		yLabel = '',
		yFormat = format(',.0f'),
		unit = '',
		annotations = [],
	}: Props = $props();

	// Use responsive width from ChartWrapper context if available
	const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
	const width = $derived(chartWidthCtx ? $chartWidthCtx : propWidth);

	const chartVisibleCtx = getContext<Writable<boolean> | undefined>('chartVisible');
	const chartVisible = $derived(chartVisibleCtx ? $chartVisibleCtx : true);

	let tooltip: TooltipData | null = $state(null);
	let tooltipDate: number | null = $state(null);

	const innerWidth = $derived(width - margin.left - margin.right);
	const innerHeight = $derived(height - margin.top - margin.bottom);

	const allDates = $derived(series.flatMap((s) => s.values.map((v) => v.date)));
	const allValues = $derived(series.flatMap((s) => s.values.map((v) => v.value)));

	const xDomain = $derived(extent(allDates) as [number, number]);
	const yDomain = $derived([
		Math.min(0, ...allValues),
		Math.max(...allValues) * 1.05,
	] as [number, number]);

	const xScale = $derived(scaleLinear().domain(xDomain).range([0, innerWidth]));
	const yScale = $derived(scaleLinear().domain(yDomain).range([innerHeight, 0]).nice());

	const colorScale = $derived(
		scaleOrdinal<string>()
			.domain(series.map((s) => s.name))
			.range(series.map((s, i) => s.color ?? CHART_COLORS[i % CHART_COLORS.length]))
	);

	const lineFn = $derived(
		d3line<{ date: number; value: number }>()
			.x((d) => xScale(d.date))
			.y((d) => yScale(d.value))
			.curve(curveMonotoneX)
	);

	const xTicks = $derived(xScale.ticks(Math.min(10, innerWidth / 80)));
	const yTicks = $derived(yScale.ticks(6));

	// End-of-line labels with collision avoidance
	const endLabels = $derived.by(() => {
		const labels = series.map((s) => {
			const last = s.values[s.values.length - 1];
			return {
				name: s.name,
				color: colorScale(s.name),
				x: last ? xScale(last.date) + 8 : 0,
				y: last ? yScale(last.value) : 0,
			};
		});
		// Sort by y position for nudging
		labels.sort((a, b) => a.y - b.y);
		const minGap = 14;
		for (let i = 1; i < labels.length; i++) {
			const diff = labels[i].y - labels[i - 1].y;
			if (diff < minGap) {
				labels[i].y = labels[i - 1].y + minGap;
			}
		}
		return labels;
	});

	function handlePointerMove(event: PointerEvent) {
		const svgEl = (event.currentTarget as SVGElement).closest('svg');
		if (!svgEl) return;
		const rect = svgEl.getBoundingClientRect();
		const mouseX = event.clientX - rect.left - margin.left;
		const date = Math.round(xScale.invert(mouseX));

		const items = series
			.map((s) => {
				const point = s.values.find((v) => v.date === date);
				if (!point) return null;
				return {
					label: s.name,
					value: yFormat(point.value),
					color: colorScale(s.name),
				};
			})
			.filter((item): item is NonNullable<typeof item> => item !== null);

		if (items.length > 0) {
			tooltip = { x: event.clientX, y: event.clientY, items };
			tooltipDate = date;
		} else {
			tooltipDate = null;
		}
	}

	function handlePointerLeave() {
		tooltip = null;
		tooltipDate = null;
	}
</script>

<svg
	class="chart"
	viewBox="0 0 {width} {height}"
	style="max-width: {width}px; width: 100%; height: auto;"
>
	<defs>
		<filter id="line-shadow" x="-2%" y="-2%" width="104%" height="104%">
			<feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity="0.08"/>
		</filter>
	</defs>
	<g transform="translate({margin.left}, {margin.top})">
		<!-- Grid lines -->
		{#each yTicks as tick}
			<line
				x1={0}
				x2={innerWidth}
				y1={yScale(tick)}
				y2={yScale(tick)}
				stroke="var(--color-border-light)"
				stroke-width="1"
			/>
		{/each}

		<!-- X axis -->
		<g transform="translate(0, {innerHeight})">
			<line x1={0} x2={innerWidth} y1={0} y2={0} stroke="var(--color-border)" />
			{#each xTicks as tick}
				<g transform="translate({xScale(tick)}, 0)">
					<line y1={0} y2={5} stroke="var(--color-border)" />
					<text y={20} text-anchor="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
						{tick}
					</text>
				</g>
			{/each}
			{#if xLabel}
				<text x={innerWidth / 2} y={36} text-anchor="middle" fill="var(--color-text-muted)" font-size="11">
					{xLabel}
				</text>
			{/if}
		</g>

		<!-- Y axis -->
		<g>
			{#each yTicks as tick}
				<text x={-8} y={yScale(tick)} text-anchor="end" dominant-baseline="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
					{yFormat(tick)}
				</text>
			{/each}
			</g>

		<!-- Annotations -->
		{#each annotations as anno}
			{@const x = xScale(anno.date)}
			{#if x >= 0 && x <= innerWidth}
				<line
					x1={x} x2={x}
					y1={0} y2={innerHeight}
					class="annotation-line"
					stroke="var(--color-text-muted)"
					stroke-width="1"
					stroke-dasharray="4 3"
					opacity="0.5"
				/>
				<text
					x={x}
					y={anno.labelPosition === 'bottom' ? innerHeight - 4 : 8}
					text-anchor="middle"
					class="annotation-label"
					fill="var(--color-text-muted)"
					font-size="9"
					font-weight="500"
					font-family="var(--font-sans)"
				>
					{anno.label}
				</text>
			{/if}
		{/each}

		<!-- Lines -->
		{#each series as s, si}
			{@const path = lineFn(s.values)}
			{#if path}
				<path
					d={path}
					fill="none"
					stroke={colorScale(s.name)}
					stroke-width="2.5"
					stroke-linejoin="round"
					stroke-linecap="round"
					shape-rendering="geometricPrecision"
					filter="url(#line-shadow)"
					stroke-dasharray="3000"
					stroke-dashoffset={chartVisible ? 0 : 3000}
					style="transition: stroke-dashoffset 1.2s cubic-bezier(0.22, 1, 0.36, 1) {si * 150}ms;"
				/>
			{/if}
		{/each}

		<!-- End-of-line labels -->
		{#each endLabels as label}
			<text
				x={label.x}
				y={label.y}
				fill={label.color}
				font-size="12"
				font-weight="500"
				dominant-baseline="middle"
				font-family="var(--font-sans)"
			>
				{label.name}
			</text>
		{/each}

		<!-- Hover crosshair + dots -->
		{#if tooltipDate !== null}
			<line
				x1={xScale(tooltipDate)}
				x2={xScale(tooltipDate)}
				y1={0}
				y2={innerHeight}
				stroke="var(--color-border)"
				stroke-width="1"
				stroke-dasharray="4,4"
				pointer-events="none"
			/>
			{#each series as s}
				{@const point = s.values.find((v) => v.date === tooltipDate)}
				{#if point}
					<circle
						cx={xScale(point.date)}
						cy={yScale(point.value)}
						r={4}
						fill={colorScale(s.name)}
						stroke="var(--color-surface)"
						stroke-width={2}
						pointer-events="none"
					/>
				{/if}
			{/each}
		{/if}

		<!-- Interaction overlay -->
		<rect
			{...{ width: innerWidth, height: innerHeight }}
			fill="transparent"
			onpointermove={handlePointerMove}
			onpointerleave={handlePointerLeave}
		/>
	</g>
</svg>

<!-- Legend -->
<div class="mt-2 flex flex-wrap gap-4 px-2 text-sm">
	{#each series as s}
		<div class="flex items-center gap-1.5">
			<span class="inline-block h-0.5 w-4 rounded" style="background: {colorScale(s.name)};"></span>
			<span class="text-text-secondary">{s.name}</span>
		</div>
	{/each}
</div>

<Tooltip data={tooltip} {unit} />
