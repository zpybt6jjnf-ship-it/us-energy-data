<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { ChartMeta } from '$types/chart';
	import { downloadCSV, downloadPNG } from '$utils/download';

	interface Props {
		meta: ChartMeta;
		data?: Record<string, unknown>[];
		children: Snippet;
	}

	let { meta, data = [], children }: Props = $props();
	let containerEl: HTMLDivElement | undefined = $state();
	let width = $state(800);

	$effect(() => {
		if (!containerEl) return;
		const observer = new ResizeObserver((entries) => {
			width = entries[0].contentRect.width;
		});
		observer.observe(containerEl);
		return () => observer.disconnect();
	});

	function handleDownloadCSV() {
		if (data.length > 0) {
			downloadCSV(data, meta.title.toLowerCase().replace(/\s+/g, '-'));
		}
	}

	async function handleDownloadPNG() {
		const svg = containerEl?.querySelector('svg.chart');
		if (svg) {
			await downloadPNG(svg as SVGSVGElement, meta.title.toLowerCase().replace(/\s+/g, '-'));
		}
	}
</script>

<div class="mb-10" bind:this={containerEl}>
	<div class="mb-4">
		<h3 class="text-lg font-semibold text-text" style="font-family: var(--font-display)">{meta.title}</h3>
		{#if meta.subtitle}
			<p class="mt-0.5 text-sm text-text-muted">{meta.subtitle}</p>
		{/if}
	</div>

	<div class="chart-container" style="width: 100%;">
		{@render children()}
	</div>

	{#if meta.description}
		<p class="mt-3 text-sm leading-relaxed text-text-secondary">{meta.description}</p>
	{/if}

	<div class="mt-3 flex flex-wrap items-center gap-4 border-t border-border-light pt-3">
		<a
			href={meta.sourceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="text-xs text-text-muted hover:text-accent transition-colors"
		>
			Source: {meta.source}
		</a>

		<button onclick={handleDownloadCSV} class="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt hover:text-text transition-colors cursor-pointer">
			<svg class="h-3.5 w-3.5" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 14V2h5l3 3v9H4z"/><path d="M9 2v3h3"/><path d="M6 8h4M6 10h4M6 12h2"/></svg>
			CSV
		</button>

		<button onclick={handleDownloadPNG} class="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt hover:text-text transition-colors cursor-pointer">
			<svg class="h-3.5 w-3.5" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="1.5"/><circle cx="6" cy="6" r="1.5"/><path d="M2 11l3-3 2 2 3-4 4 5"/></svg>
			PNG
		</button>

		{#if meta.lastUpdated}
			<span class="ml-auto text-xs text-text-muted">Updated: {meta.lastUpdated}</span>
		{/if}
	</div>

	{#if meta.caveats}
		<p class="mt-2 text-xs italic text-text-muted">{meta.caveats}</p>
	{/if}
</div>
