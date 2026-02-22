<script lang="ts">
	import { updateConfig } from '$stores/chartConfig';

	interface Props {
		min?: number;
		max?: number;
		startYear: number;
		endYear: number;
	}

	let { min = 2001, max = 2024, startYear, endYear }: Props = $props();

	const startOptions = $derived(
		Array.from({ length: endYear - min }, (_, i) => min + i)
	);

	const endOptions = $derived(
		Array.from({ length: max - startYear }, (_, i) => startYear + 1 + i)
	);

	function handleStartChange(e: Event) {
		const val = Number((e.target as HTMLSelectElement).value);
		updateConfig('start', val);
	}

	function handleEndChange(e: Event) {
		const val = Number((e.target as HTMLSelectElement).value);
		updateConfig('end', val);
	}
</script>

<div class="inline-flex items-center gap-2">
	<span class="text-sm font-medium text-text-secondary">Years</span>
	<div class="relative">
		<select
			value={startYear}
			onchange={handleStartChange}
			class="appearance-none rounded-lg border border-border bg-surface-card pl-3 pr-8 py-1.5 text-sm font-medium text-text shadow-sm hover:border-accent/40 focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none transition-colors cursor-pointer"
		>
			{#each startOptions as year}
				<option value={year} selected={year === startYear}>{year}</option>
			{/each}
		</select>
		<svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6l4 4 4-4"/></svg>
	</div>
	<span class="text-sm text-text-muted">—</span>
	<div class="relative">
		<select
			value={endYear}
			onchange={handleEndChange}
			class="appearance-none rounded-lg border border-border bg-surface-card pl-3 pr-8 py-1.5 text-sm font-medium text-text shadow-sm hover:border-accent/40 focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none transition-colors cursor-pointer"
		>
			{#each endOptions as year}
				<option value={year} selected={year === endYear}>{year}</option>
			{/each}
		</select>
		<svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6l4 4 4-4"/></svg>
	</div>
</div>
