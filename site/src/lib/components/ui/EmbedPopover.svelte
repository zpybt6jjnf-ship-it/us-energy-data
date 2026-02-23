<script lang="ts">
	interface Props {
		chartId: string;
	}

	let { chartId }: Props = $props();
	let copied = $state(false);

	const embedUrl = $derived(
		typeof window !== 'undefined'
			? `${window.location.origin}${window.location.pathname}?embed=true#${chartId}`
			: ''
	);

	const snippet = $derived(
		`<iframe src="${embedUrl}" width="100%" height="600" style="border:none;" loading="lazy" title="${chartId}"></iframe>`
	);

	async function copySnippet() {
		try {
			await navigator.clipboard.writeText(snippet);
		} catch {
			const ta = document.createElement('textarea');
			ta.value = snippet;
			document.body.appendChild(ta);
			ta.select();
			document.execCommand('copy');
			document.body.removeChild(ta);
		}
		copied = true;
		setTimeout(() => { copied = false; }, 2000);
	}
</script>

<div class="absolute right-0 top-full z-50 mt-1 w-80 rounded-lg border border-border bg-surface-card p-3 shadow-lg">
	<p class="text-xs font-medium text-text-secondary mb-2">Embed this chart</p>
	<pre class="text-[10px] font-mono text-text bg-surface-alt rounded p-2 overflow-x-auto whitespace-pre-wrap break-all leading-relaxed">{snippet}</pre>
	<button
		onclick={copySnippet}
		class="mt-2 w-full rounded-md bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent-dark transition-colors cursor-pointer"
	>
		{copied ? 'Copied!' : 'Copy embed code'}
	</button>
</div>
