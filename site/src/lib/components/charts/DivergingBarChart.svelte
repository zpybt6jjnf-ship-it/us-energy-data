<script lang="ts">
    import { scaleBand, scaleLinear } from 'd3-scale';
    import { format } from 'd3-format';
    import type { Margin, TooltipData } from '$types/chart';
    import { SEMANTIC_COLORS } from '$utils/colors';
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
        yFormat?: (v: number) => string;
        unit?: string;
        positiveColor?: string;
        negativeColor?: string;
        positiveLabel?: string;
        negativeLabel?: string;
    }

    let {
        data,
        width: propWidth = 800,
        height: propHeight = 400,
        margin = { top: 16, right: 20, bottom: 40, left: 60 },
        yFormat = format('+,.0f'),
        unit = '',
        positiveColor = SEMANTIC_COLORS.positive,
        negativeColor = SEMANTIC_COLORS.negative,
        positiveLabel = 'Growth',
        negativeLabel = 'Decline',
    }: Props = $props();

    const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
    const chartHeightCtx = getContext<Readable<number> | undefined>('chartHeight');
    const width = $derived(chartWidthCtx ? ($chartWidthCtx ?? propWidth) : propWidth);
    const height = $derived(chartHeightCtx ? ($chartHeightCtx ?? propHeight) : propHeight);

    const chartVisibleCtx = getContext<Writable<boolean> | undefined>('chartVisible');
    const chartVisible = $derived(chartVisibleCtx ? $chartVisibleCtx : true);

    const chartTitleCtx = getContext<Readable<string> | undefined>('chartTitle');
    const chartTitle = $derived(chartTitleCtx ? $chartTitleCtx : '');

    let tooltip: TooltipData | null = $state(null);
    let hoveredIndex: number | null = $state(null);
    let svgEl: SVGSVGElement | undefined = $state();

    const innerWidth = $derived(width - margin.left - margin.right);
    const innerHeight = $derived(height - margin.top - margin.bottom);

    const xScale = $derived(
        scaleBand<string>()
            .domain(data.map((d) => d.label))
            .range([0, innerWidth])
            .padding(0.15)
    );

    const maxAbs = $derived(Math.max(...data.map((d) => Math.abs(d.value)), 1));

    const yScale = $derived(
        scaleLinear()
            .domain([-maxAbs * 1.1, maxAbs * 1.1])
            .range([innerHeight, 0])
            .nice()
    );

    const yTicks = $derived(yScale.ticks(Math.min(6, Math.floor(innerHeight / 50))));
    const zeroY = $derived(yScale(0));

    // Label thinning: show every Nth label so they don't overlap
    const xLabelSkip = $derived.by(() => {
        if (data.length === 0) return 1;
        const maxLabelLen = Math.max(...data.map((d) => d.label.length));
        const charWidth = 7; // ~7px per char at font-size 11
        const labelSpace = maxLabelLen * charWidth + 8; // + padding
        const step = xScale.step();
        return Math.max(1, Math.ceil(labelSpace / step));
    });

    function handleBarHover(event: PointerEvent, d: BarData, index: number) {
        hoveredIndex = index;
        const barColor = d.value >= 0 ? (d.color ?? positiveColor) : (d.color ?? negativeColor);
        tooltip = {
            x: event.clientX,
            y: event.clientY,
            header: d.label,
            subtitle: unit || undefined,
            items: [{
                label: yFormat(d.value),
                value: unit || '',
                color: barColor,
            }],
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
        const bandPos = xScale(d.label) ?? 0;
        const bandWidth = xScale.bandwidth();
        const barColor = d.value >= 0 ? (d.color ?? positiveColor) : (d.color ?? negativeColor);
        hoveredIndex = index;
        tooltip = {
            x: rect.left + margin.left + bandPos + bandWidth / 2,
            y: rect.top + margin.top + yScale(d.value),
            header: d.label,
            subtitle: unit || undefined,
            items: [{ label: yFormat(d.value), value: unit || '', color: barColor }],
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

{#if data.length > 0}
<!-- svelte-ignore a11y_no_noninteractive_tabindex a11y_no_noninteractive_element_interactions -->
<svg
    bind:this={svgEl}
    class="chart"
    viewBox="0 0 {width} {height}"
    style="max-width: {width}px; width: 100%; height: auto; outline-offset: 2px;"
    role="figure"
    aria-label={chartTitle || `Diverging bar chart showing ${data.length} values`}
    tabindex="0"
    onkeydown={handleKeydown}
    onfocusout={handleFocusOut}
>
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

        <!-- Zero baseline -->
        <line
            x1={0}
            x2={innerWidth}
            y1={zeroY}
            y2={zeroY}
            stroke="var(--color-text-secondary)"
            stroke-width="1.5"
        />

        <!-- Bars -->
        {#each data as d, i}
            {@const barX = xScale(d.label) ?? 0}
            {@const barWidth = xScale.bandwidth()}
            {@const barColor = d.value >= 0 ? (d.color ?? positiveColor) : (d.color ?? negativeColor)}
            {@const targetY = d.value >= 0 ? yScale(d.value) : zeroY}
            {@const targetHeight = Math.abs(yScale(d.value) - zeroY)}
            {@const isHovered = hoveredIndex === i}
            <rect
                x={barX}
                y={chartVisible ? targetY : zeroY}
                width={barWidth}
                height={chartVisible ? targetHeight : 0}
                fill={barColor}
                fill-opacity={hoveredIndex === null ? 0.85 : isHovered ? 1 : 0.4}
                stroke={isHovered ? 'var(--color-accent)' : 'none'}
                stroke-width={isHovered ? 1.5 : 0}
                rx="1"
                style="transition: y 0.5s cubic-bezier(0.22, 1, 0.36, 1) {i * 50}ms, height 0.5s cubic-bezier(0.22, 1, 0.36, 1) {i * 50}ms, fill-opacity 0.15s ease, stroke 0.15s ease;"
                onpointermove={(e) => handleBarHover(e, d, i)}
                onpointerleave={handlePointerLeave}
            />
        {/each}

        <!-- X axis labels (thinned to avoid overlap) -->
        <g transform="translate(0, {innerHeight})">
            <line x1={0} x2={innerWidth} stroke="var(--color-border)" />
            {#each data as d, i}
                {#if i % xLabelSkip === 0}
                    <text
                        x={(xScale(d.label) ?? 0) + xScale.bandwidth() / 2}
                        y={16}
                        text-anchor="middle"
                        fill="var(--color-text-secondary)"
                        font-size="11"
                        font-family="var(--font-mono)"
                    >
                        {d.label}
                    </text>
                {/if}
            {/each}
        </g>

        <!-- Y axis labels -->
        {#each yTicks as tick}
            <text
                x={-8}
                y={yScale(tick)}
                text-anchor="end"
                dominant-baseline="middle"
                fill="var(--color-text-secondary)"
                font-size="13"
                font-family="var(--font-mono)"
            >
                {yFormat(tick)}
            </text>
        {/each}
    </g>
</svg>

<!-- +/- Legend -->
<div class="mt-1 flex flex-wrap gap-4 px-2 text-xs">
    <div class="flex items-center gap-1.5">
        <span class="inline-block h-2.5 w-2.5 rounded-full" style="background: {positiveColor};"></span>
        <span class="text-text-secondary">{positiveLabel}</span>
    </div>
    <div class="flex items-center gap-1.5">
        <span class="inline-block h-2.5 w-2.5 rounded-full" style="background: {negativeColor};"></span>
        <span class="text-text-secondary">{negativeLabel}</span>
    </div>
</div>

<Tooltip data={tooltip} />
{:else}
<p class="text-sm text-text-muted py-12 text-center">No data available</p>
{/if}
