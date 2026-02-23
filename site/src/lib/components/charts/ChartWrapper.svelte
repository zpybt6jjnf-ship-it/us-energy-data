<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { ChartMeta } from '$types/chart';
	import { downloadCSV, downloadPNG } from '$utils/download';
	import { setContext } from 'svelte';
	import { writable } from 'svelte/store';

	interface Props {
		meta: ChartMeta;
		data?: Record<string, unknown>[];
		hero?: boolean;
		children: Snippet;
	}

	let { meta, data = [], hero = false, children }: Props = $props();
	let containerEl: HTMLDivElement | undefined = $state();
	let width = $state(800);
	let visible = $state(false);
	let linkCopied = $state(false);

	const chartWidth = writable(800);
	setContext('chartWidth', chartWidth);

	const chartHeight = writable(400);
	setContext('chartHeight', chartHeight);

	const chartVisible = writable(false);
	setContext('chartVisible', chartVisible);

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
</script>

<div
	class="chart-card relative"
	bind:this={containerEl}
>
	<div class="mb-2">
		<h3 class="text-[13px] font-bold font-display tracking-tight text-text">{meta.title}</h3>
		{#if meta.subtitle}
			<p class="mt-0.5 text-xs text-text-muted">{meta.subtitle}</p>
		{/if}
	</div>

	{#if !visible}
		<div class="skeleton" style="width: 100%; height: 300px;"></div>
	{:else}
		<div class="chart-container" style="width: 100%; opacity: {visible ? 1 : 0}; transform: translateY({visible ? 0 : 20}px); transition: opacity 0.5s ease-out, transform 0.5s ease-out;">
			{@render children()}
		</div>
	{/if}

	<div class="mt-2 flex flex-wrap items-center gap-1 px-0.5 py-1">
		<a
			href={meta.sourceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="text-[11px] text-text-muted hover:text-accent no-underline transition-colors"
		>
			Source: {meta.source}
		</a>

		<button onclick={handleDownloadCSV} class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium text-text-muted hover:bg-surface-alt hover:text-accent hover:border-accent/30 border border-transparent transition-colors cursor-pointer">
			<svg class="h-3 w-3" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 14V2h5l3 3v9H4z"/><path d="M9 2v3h3"/><path d="M6 8h4M6 10h4M6 12h2"/></svg>
			CSV
		</button>

		<button onclick={handleDownloadPNG} class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium text-text-muted hover:bg-surface-alt hover:text-accent hover:border-accent/30 border border-transparent transition-colors cursor-pointer">
			<svg class="h-3 w-3" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="1.5"/><circle cx="6" cy="6" r="1.5"/><path d="M2 11l3-3 2 2 3-4 4 5"/></svg>
			PNG
		</button>

		<button onclick={handleCopyLink} class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium text-text-muted hover:bg-surface-alt hover:text-accent hover:border-accent/30 border border-transparent transition-colors cursor-pointer">
			<svg class="h-3 w-3" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6.5 9.5l3-3M5.5 7l-1 1a2.12 2.12 0 003 3l1-1M10.5 9l1-1a2.12 2.12 0 00-3-3l-1 1"/></svg>
			{linkCopied ? 'Copied!' : 'Link'}
		</button>

		{#if meta.lastUpdated}
			<span class="ml-auto text-[11px] text-text-muted">Updated: {meta.lastUpdated}</span>
		{/if}
	</div>

	{#if meta.description || meta.caveats}
		<details class="mt-0.5 group">
			<summary class="flex cursor-pointer items-center gap-1 text-[11px] font-medium text-text-muted hover:text-text-secondary transition-colors list-none">
				<svg class="h-3 w-3 transition-transform group-open:rotate-90" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4l4 4-4 4"/></svg>
				About this chart
			</summary>
			{#if meta.description}
				<p class="mt-1.5 text-[11px] leading-relaxed text-text-secondary">{meta.description}</p>
			{/if}
			{#if meta.caveats}
				<p class="mt-1.5 text-[11px] italic text-text-muted leading-relaxed">{meta.caveats}</p>
			{/if}
		</details>
	{/if}
</div>

<style>
	@keyframes skeleton-shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}
</style>
