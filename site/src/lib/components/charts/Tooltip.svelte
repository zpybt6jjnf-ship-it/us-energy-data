<script lang="ts">
	import type { TooltipData } from '$types/chart';
	import { formatNumber } from '$utils/formatting';

	interface Props {
		data: TooltipData | null;
		unit?: string;
	}

	let { data, unit = '' }: Props = $props();

	let tooltipEl: HTMLDivElement | undefined = $state();
	let visible = $state(false);

	const TOOLTIP_WIDTH_ESTIMATE = 180;
	const OFFSET = 12;

	let tooltipLeft = $derived.by(() => {
		if (!data) return 0;
		const width = tooltipEl?.offsetWidth ?? TOOLTIP_WIDTH_ESTIMATE;
		if (data.x + width + OFFSET > (typeof window !== 'undefined' ? window.innerWidth : 9999)) {
			return data.x - width - OFFSET;
		}
		return data.x + OFFSET;
	});

	$effect(() => {
		if (data) {
			// Trigger enter transition on next frame
			visible = false;
			requestAnimationFrame(() => { visible = true; });
		} else {
			visible = false;
		}
	});
</script>

{#if data}
	<div
		bind:this={tooltipEl}
		class="pointer-events-none fixed z-50 rounded-lg border border-border px-2.5 py-1.5 shadow-xl"
		style="left: {tooltipLeft}px; top: {data.y - 8}px; opacity: {visible ? 1 : 0}; transform: translateY({visible ? 0 : 4}px); transition: opacity 0.15s ease, transform 0.15s ease; font-size: 11px; background: var(--color-surface-card, rgba(18,22,31,0.95)); backdrop-filter: blur(12px);"
	>
		{#if data.header}
			<div class="mb-1 text-xs font-bold text-text" style="font-family: var(--font-mono)">{data.header}</div>
		{/if}
		{#each data.items as item}
			<div class="flex items-center gap-2 whitespace-nowrap">
				<span
					class="inline-block h-2.5 w-2.5 rounded-full"
					style="background: {item.color};"
				></span>
				<span class="text-text-muted">{item.label}</span>
				<span class="font-semibold text-text" style="font-family: var(--font-mono)">{item.value}{unit ? ` ${unit}` : ''}</span>
			</div>
		{/each}
	</div>
{/if}
