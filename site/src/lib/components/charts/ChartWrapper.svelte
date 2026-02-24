<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { ChartMeta } from '$types/chart';
	import { downloadCSV, downloadPNG } from '$utils/download';
	import { setContext } from 'svelte';
	import { writable } from 'svelte/store';
	import DataTable from './DataTable.svelte';
	import EmbedPopover from '$components/ui/EmbedPopover.svelte';

	interface Props {
		meta: ChartMeta;
		data?: Record<string, unknown>[];
		children: Snippet;
		controls?: Snippet;
		allowLogScale?: boolean;
	}

	let { meta, data = [], children, controls, allowLogScale = false }: Props = $props();
	let containerEl: HTMLDivElement | undefined = $state();
	let width = $state(800);
	let visible = $state(false);
	let linkCopied = $state(false);
	let isFullscreen = $state(false);
	let showTable = $state(false);
	let showEmbed = $state(false);

	const chartWidth = writable(800);
	setContext('chartWidth', chartWidth);

	const chartHeight = writable(400);
	setContext('chartHeight', chartHeight);

	const chartVisible = writable(false);
	setContext('chartVisible', chartVisible);

	const chartTitle = writable('');
	setContext('chartTitle', chartTitle);
	$effect(() => { chartTitle.set(meta.title); });

	// Log scale context
	const chartLogScale = writable(false);
	setContext('chartLogScale', chartLogScale);

	$effect(() => {
		if (!containerEl) return;
		const observer = new ResizeObserver((entries) => {
			width = entries[0].contentRect.width;
			chartWidth.set(width);
			chartHeight.set(Math.max(280, Math.min(480, Math.round(width * 0.5))));
		});
		observer.observe(containerEl);
		return () => observer.disconnect();
	});

	$effect(() => {
		if (!containerEl) return;
		const io = new IntersectionObserver(
			(entries) => {
				if (entries[0].isIntersecting) {
					visible = true;
					chartVisible.set(true);
					io.disconnect();
				}
			},
			{ threshold: 0.15 }
		);
		io.observe(containerEl);
		return () => io.disconnect();
	});

	function handleDownloadCSV() {
		if (data.length > 0) {
			downloadCSV(data, meta.title.toLowerCase().replace(/\s+/g, '-'));
		}
	}

	async function handleDownloadPNG() {
		const svg = containerEl?.querySelector('svg.chart');
		if (svg) {
			await downloadPNG(
				svg as SVGSVGElement,
				meta.title.toLowerCase().replace(/\s+/g, '-'),
				{ title: meta.title, source: meta.source }
			);
		}
	}

	async function handleFullscreen() {
		if (!containerEl) return;
		if (document.fullscreenElement) {
			await document.exitFullscreen();
		} else {
			await containerEl.requestFullscreen();
		}
	}

	$effect(() => {
		function onFullscreenChange() {
			isFullscreen = !!document.fullscreenElement;
		}
		document.addEventListener('fullscreenchange', onFullscreenChange);
		return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
	});

	async function handleCopyLink() {
		try {
			await navigator.clipboard.writeText(window.location.href);
			linkCopied = true;
			setTimeout(() => { linkCopied = false; }, 2000);
		} catch {
			const input = document.createElement('input');
			input.value = window.location.href;
			document.body.appendChild(input);
			input.select();
			document.execCommand('copy');
			document.body.removeChild(input);
			linkCopied = true;
			setTimeout(() => { linkCopied = false; }, 2000);
		}
	}

	const chartId = $derived(meta.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''));

	function toggleLogScale() {
		chartLogScale.update((v) => !v);
	}

	const hasMethodology = $derived(!!(meta.description || meta.caveats));
</script>

<div
	class="relative py-6"
	class:fullscreen-container={isFullscreen}
	bind:this={containerEl}
>
	<div class="mb-3">
		<h3 class="text-lg font-serif tracking-normal text-text">{meta.title}</h3>
		{#if meta.subtitle}
			<p class="mt-0.5 text-sm text-text-muted">{meta.subtitle}</p>
		{/if}
	</div>

	{#if controls || allowLogScale || data.length > 0}
		<div class="mb-2 flex flex-wrap items-center gap-2">
			{#if controls}
				{@render controls()}
			{/if}

			{#if allowLogScale}
				<button
					onclick={toggleLogScale}
					class="rounded border border-border px-2 py-0.5 text-[11px] font-medium transition-colors cursor-pointer {$chartLogScale ? 'bg-accent text-white border-accent' : 'bg-transparent text-text-secondary hover:border-accent hover:text-accent'}"
					aria-label="Toggle logarithmic scale"
				>
					{$chartLogScale ? 'Log' : 'Lin'}
				</button>
			{/if}
		</div>
	{/if}

	{#if !visible}
		<div class="skeleton" style="width: 100%; height: {$chartHeight}px;"></div>
	{:else if showTable && data.length > 0}
		<DataTable {data} unit={meta.unit} />
	{:else}
		<div class="chart-container" style="width: 100%; opacity: {visible ? 1 : 0}; transform: translateY({visible ? 0 : 20}px); transition: opacity 0.5s ease-out, transform 0.5s ease-out;">
			{@render children()}
		</div>
	{/if}

	<div class="mt-3 flex flex-wrap items-center gap-2 px-0.5 py-1">
		<a
			href={meta.sourceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="text-[11px] text-text-muted hover:text-accent no-underline transition-colors"
		>
			Source: {meta.source}
		</a>

		<span class="text-text-muted/30 text-[11px]">·</span>

		{#if data.length > 0}
			<button onclick={() => { showTable = !showTable; }} aria-label={showTable ? 'Show chart' : 'Show data table'} class="text-[11px] text-text-muted hover:text-accent transition-colors cursor-pointer bg-transparent border-none p-0">
				{showTable ? 'Chart' : 'Table'}
			</button>

			<span class="text-text-muted/30 text-[11px]">·</span>
		{/if}

		<button onclick={handleDownloadCSV} aria-label="Download data as CSV" class="text-[11px] text-text-muted transition-colors bg-transparent border-none p-0 {data.length > 0 ? 'hover:text-accent cursor-pointer' : 'opacity-40 cursor-not-allowed'}" disabled={data.length === 0}>
			CSV
		</button>

		<span class="text-text-muted/30 text-[11px]">·</span>

		<button onclick={handleDownloadPNG} aria-label="Download chart as PNG" class="text-[11px] text-text-muted transition-colors bg-transparent border-none p-0 {data.length > 0 ? 'hover:text-accent cursor-pointer' : 'opacity-40 cursor-not-allowed'}" disabled={data.length === 0}>
			PNG
		</button>

		<span class="text-text-muted/30 text-[11px]">·</span>

		<button onclick={handleCopyLink} aria-label="Copy link to chart" class="text-[11px] text-text-muted hover:text-accent transition-colors cursor-pointer bg-transparent border-none p-0">
			{linkCopied ? 'Copied!' : 'Link'}
		</button>

		<span class="text-text-muted/30 text-[11px]">·</span>

		<div class="relative inline-block">
			<button onclick={() => { showEmbed = !showEmbed; }} aria-label="Get embed code" class="text-[11px] text-text-muted hover:text-accent transition-colors cursor-pointer bg-transparent border-none p-0">
				&lt;/&gt;
			</button>
			{#if showEmbed}
				<EmbedPopover {chartId} />
			{/if}
		</div>

		<span class="text-text-muted/30 text-[11px]">·</span>

		<button onclick={handleFullscreen} aria-label={isFullscreen ? 'Exit fullscreen' : 'View chart fullscreen'} class="text-[11px] text-text-muted hover:text-accent transition-colors cursor-pointer bg-transparent border-none p-0">
			{isFullscreen ? '⤓' : '⤢'}
		</button>

		{#if meta.lastUpdated}
			<span class="ml-auto text-[11px] text-text-muted">Updated: {meta.lastUpdated}</span>
		{/if}
	</div>

	{#if hasMethodology}
		<details class="mt-2">
			<summary class="text-[12px] font-medium text-text-secondary cursor-pointer select-none hover:text-accent transition-colors">
				Sources & methodology
			</summary>
			<div class="mt-1.5 pl-3 border-l-2 border-border-light">
				{#if meta.description}
					<p class="text-[12px] leading-relaxed text-text-secondary">{meta.description}</p>
				{/if}
				{#if meta.caveats}
					<p class="mt-1.5 text-[12px] italic text-text-muted leading-relaxed">{meta.caveats}</p>
				{/if}
			</div>
		</details>
	{/if}

	{#if meta.relatedCharts && meta.relatedCharts.length > 0}
		<div class="mt-3 flex flex-wrap items-center gap-1.5">
			<span class="text-[11px] text-text-muted">Related:</span>
			{#each meta.relatedCharts as related}
				<a
					href={related.href}
					class="inline-block rounded-full border border-border px-2.5 py-0.5 text-[11px] font-medium text-text-secondary hover:border-accent hover:text-accent no-underline transition-colors"
				>
					{related.title}
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	@keyframes skeleton-shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}
	.fullscreen-container {
		background: var(--color-surface);
		padding: 2rem;
		display: flex;
		flex-direction: column;
		justify-content: center;
	}
</style>
