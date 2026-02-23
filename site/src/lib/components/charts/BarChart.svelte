<script lang="ts">
	import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
	import { format } from 'd3-format';
	import type { Margin, TooltipData } from '$types/chart';
	import { CHART_COLORS } from '$utils/colors';
	import Tooltip from './Tooltip.svelte';
	import { getContext } from 'svelte';
	import type { Readable, Writable } from 'svelte/store';

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
		width: propWidth = 800,
		height: propHeight = 400,
		margin = { top: 16, right: 16, bottom: 48, left: 52 },
		horizontal = false,
		xLabel = '',
		yLabel = '',
		yFormat = format(',.0f'),
		unit = '',
	}: Props = $props();

	const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
	const chartHeightCtx = getContext<Readable<number> | undefined>('chartHeight');
	const width = $derived(chartWidthCtx ? $chartWidthCtx : propWidth);
	const height = $derived(chartHeightCtx ? $chartHeightCtx : propHeight);

	const chartVisibleCtx = getContext<Writable<boolean> | undefined>('chartVisible');
	const chartVisible = $derived(chartVisibleCtx ? $chartVisibleCtx : true);

	const chartTitleCtx = getContext<Readable<string> | undefined>('chartTitle');
	const chartTitle = $derived(chartTitleCtx ? $chartTitleCtx : '');

	let tooltip: TooltipData | null = $state(null);
	let hoveredIndex: number | null = $state(null);
	let svgEl: SVGSVGElement | undefined = $state();

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
			header: d.label,
			subtitle: unit || undefined,
			items: [{ label: yFormat(d.value), value: unit || '', color: colorScale(d.label) }],
		};
	}

	function handlePointerLeave() {
		hoveredIndex = null;
		tooltip = null;
	}

	function updateTooltipForIndex(index: number) {
		const d = data[index];
		if (!d || !svgEl) return;
		const rect = svgEl.getBoundingClientRect();
		const bandPos = bandScale(d.label) ?? 0;
		const bandWidth = bandScale.bandwidth();
		hoveredIndex = index;
		tooltip = {
			x: rect.left + margin.left + (horizontal ? valueScale(d.value) / 2 : bandPos + bandWidth / 2),
			y: rect.top + margin.top + (horizontal ? bandPos + bandWidth / 2 : valueScale(d.value)),
			header: d.label,
			subtitle: unit || undefined,
			items: [{ label: yFormat(d.value), value: unit || '', color: colorScale(d.label) }],
		};
	}

	function handleKeydown(event: KeyboardEvent) {
		if (data.length === 0) return;

		if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
			event.preventDefault();
			const next = hoveredIndex === null ? 0 : Math.min(hoveredIndex + 1, data.length - 1);
			updateTooltipForIndex(next);
		} else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
			event.preventDefault();
			const prev = hoveredIndex === null ? data.length - 1 : Math.max(hoveredIndex - 1, 0);
			updateTooltipForIndex(prev);
		} else if (event.key === 'Escape') {
			hoveredIndex = null;
			tooltip = null;
			svgEl?.blur();
		}
	}

	function handleFocusOut() {
		hoveredIndex = null;
		tooltip = null;
	}
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex a11y_no_noninteractive_element_interactions -->
<svg
	bind:this={svgEl}
	class="chart"
	viewBox="0 0 {width} {height}"
	style="max-width: {width}px; width: 100%; height: auto; outline-offset: 2px;"
	role="img"
	aria-label={chartTitle || `Bar chart showing ${data.map(d => d.label).join(', ')}`}
	tabindex="0"
	onkeydown={handleKeydown}
	onfocusout={handleFocusOut}
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
					stroke="var(--color-border-light)"
				/>
			{:else}
				<line
					x1={0}
					x2={innerWidth}
					y1={valueScale(tick)}
					y2={valueScale(tick)}
					stroke="var(--color-border-light)"
				/>
			{/if}
		{/each}

		<!-- Bars -->
		{#each data as d, i}
			{@const bandPos = bandScale(d.label) ?? 0}
			{@const bandWidth = bandScale.bandwidth()}
			{@const barOpacity = hoveredIndex === null ? 1 : hoveredIndex === i ? 1 : 0.4}
			{@const isHovered = hoveredIndex === i}
			{#if horizontal}
				<rect
					x={0}
					y={bandPos}
					width={chartVisible ? valueScale(d.value) : 0}
					height={bandWidth}
					fill={colorScale(d.label)}
					rx="3"
					shape-rendering="crispEdges"
					opacity={barOpacity}
					stroke={isHovered ? 'var(--color-accent)' : 'none'}
					stroke-width={isHovered ? 1.5 : 0}
					style="transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1) {i * 50}ms, opacity 0.2s ease, stroke 0.15s ease;"
					onpointermove={(e) => handleBarHover(e, d, i)}
					onpointerleave={handlePointerLeave}
				/>
			{:else}
				<rect
					x={bandPos}
					y={chartVisible ? valueScale(d.value) : innerHeight}
					width={bandWidth}
					height={chartVisible ? innerHeight - valueScale(d.value) : 0}
					fill={colorScale(d.label)}
					rx="3"
					shape-rendering="crispEdges"
					opacity={barOpacity}
					stroke={isHovered ? 'var(--color-accent)' : 'none'}
					stroke-width={isHovered ? 1.5 : 0}
					style="transition: y 0.5s cubic-bezier(0.22, 1, 0.36, 1) {i * 50}ms, height 0.5s cubic-bezier(0.22, 1, 0.36, 1) {i * 50}ms, opacity 0.2s ease, stroke 0.15s ease;"
					onpointermove={(e) => handleBarHover(e, d, i)}
					onpointerleave={handlePointerLeave}
				/>
			{/if}
		{/each}

		<!-- Axes -->
		{#if horizontal}
			<!-- Value axis (bottom) -->
			<g transform="translate(0, {innerHeight})">
				<line x1={0} x2={innerWidth} stroke="var(--color-border)" />
				{#each valueTicks as tick}
					<text x={valueScale(tick)} y={20} text-anchor="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
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
					fill="var(--color-text-secondary)"
					font-size="13"
				>
					{d.label}
				</text>
			{/each}
		{:else}
			<!-- Value axis (left) -->
			{#each valueTicks as tick}
				<text x={-8} y={valueScale(tick)} text-anchor="end" dominant-baseline="middle" fill="var(--color-text-secondary)" font-size="13" font-family="var(--font-mono)">
					{yFormat(tick)}
				</text>
			{/each}
			<!-- Category axis (bottom) -->
			<g transform="translate(0, {innerHeight})">
				<line x1={0} x2={innerWidth} stroke="var(--color-border)" />
				{#each data as d}
					{@const maxChars = Math.max(3, Math.floor(bandScale.bandwidth() / 8))}
					<text
						x={(bandScale(d.label) ?? 0) + bandScale.bandwidth() / 2}
						y={20}
						text-anchor="middle"
						fill="var(--color-text-secondary)"
						font-size="13"
						class="truncate"
					>
						{d.label.length > maxChars ? d.label.slice(0, maxChars - 1) + '\u2026' : d.label}
					</text>
				{/each}
			</g>
		{/if}

	</g>
</svg>

<!-- Legend for multi-colored bars -->
{#if hasMultipleColors}
	<div class="mt-1 flex flex-wrap gap-4 px-2 text-xs">
		{#each data as d, i}
			<div class="flex items-center gap-1.5">
				<span class="inline-block h-2.5 w-2.5 rounded" style="background: {colorScale(d.label)};"></span>
				<span class="text-text-secondary">{d.label}</span>
			</div>
		{/each}
	</div>
{/if}

<Tooltip data={tooltip} />
