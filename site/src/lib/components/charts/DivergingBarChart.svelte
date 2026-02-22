<script lang="ts">
    import { scaleBand, scaleLinear } from 'd3-scale';
    import { format } from 'd3-format';
    import type { Margin, TooltipData } from '$types/chart';
    import Tooltip from './Tooltip.svelte';
    import { getContext } from 'svelte';
    import type { Readable } from 'svelte/store';

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
        yLabel?: string;
        yFormat?: (v: number) => string;
        unit?: string;
        positiveColor?: string;
        negativeColor?: string;
    }

    let {
        data,
        width: propWidth = 800,
        height: propHeight = 400,
        margin = { top: 16, right: 20, bottom: 40, left: 60 },
        yLabel = '',
        yFormat = format('+,.0f'),
        unit = '',
        positiveColor = '#1b9e77',
        negativeColor = '#e31a1c',
    }: Props = $props();

    const chartWidthCtx = getContext<Readable<number> | undefined>('chartWidth');
    const chartHeightCtx = getContext<Readable<number> | undefined>('chartHeight');
    const width = $derived(chartWidthCtx ? $chartWidthCtx : propWidth);
    const height = $derived(chartHeightCtx ? $chartHeightCtx : propHeight);

    let tooltip: TooltipData | null = $state(null);
    let hoveredIndex: number | null = $state(null);

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

    const yTicks = $derived(yScale.ticks(6));
    const zeroY = $derived(yScale(0));

    function handleBarHover(event: PointerEvent, d: BarData, index: number) {
        hoveredIndex = index;
        tooltip = {
            x: event.clientX,
            y: event.clientY,
            items: [{
                label: d.label,
                value: yFormat(d.value),
                color: d.value >= 0 ? (d.color ?? positiveColor) : (d.color ?? negativeColor),
            }],
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
    role="img"
    aria-label="Diverging bar chart showing {data.length} values"
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
            {@const barY = d.value >= 0 ? yScale(d.value) : zeroY}
            {@const barHeight = Math.abs(yScale(d.value) - zeroY)}
            {@const isHovered = hoveredIndex === i}
            <rect
                x={barX}
                y={barY}
                width={barWidth}
                height={barHeight}
                fill={barColor}
                fill-opacity={hoveredIndex === null ? 0.85 : isHovered ? 1 : 0.4}
                rx="1"
                style="transition: fill-opacity 0.15s ease;"
                onpointermove={(e) => handleBarHover(e, d, i)}
                onpointerleave={handlePointerLeave}
            />
        {/each}

        <!-- X axis labels -->
        <g transform="translate(0, {innerHeight})">
            <line x1={0} x2={innerWidth} stroke="var(--color-border)" />
            {#each data as d}
                {@const x = (xScale(d.label) ?? 0) + xScale.bandwidth() / 2}
                <text
                    {x}
                    y={16}
                    text-anchor="middle"
                    fill="var(--color-text-secondary)"
                    font-size="11"
                    font-family="var(--font-mono)"
                >
                    {d.label}
                </text>
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

<Tooltip data={tooltip} {unit} />
