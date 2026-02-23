<script lang="ts">
	interface Props {
		mode: 'map' | 'chart';
		onToggle: (mode: 'map' | 'chart') => void;
	}

	let { mode, onToggle }: Props = $props();
</script>

<div class="inline-flex rounded-lg border border-border overflow-hidden" role="group" aria-label="View mode">
	<button
		type="button"
		class="px-2.5 py-1 text-[11px] font-medium transition-colors cursor-pointer {mode === 'map' ? 'bg-accent text-white' : 'bg-transparent text-text-secondary hover:text-accent'}"
		onclick={() => onToggle('map')}
		aria-pressed={mode === 'map'}
	>
		<svg class="inline-block h-3 w-3 mr-0.5 -mt-px" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
			<rect x="1" y="3" width="14" height="10" rx="1" />
			<path d="M5.5 3v10M10.5 3v10" />
		</svg>
		Map
	</button>
	<button
		type="button"
		class="px-2.5 py-1 text-[11px] font-medium transition-colors cursor-pointer border-l border-border {mode === 'chart' ? 'bg-accent text-white' : 'bg-transparent text-text-secondary hover:text-accent'}"
		onclick={() => onToggle('chart')}
		aria-pressed={mode === 'chart'}
	>
		<svg class="inline-block h-3 w-3 mr-0.5 -mt-px" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
			<rect x="2" y="8" width="3" height="5" />
			<rect x="6.5" y="5" width="3" height="8" />
			<rect x="11" y="2" width="3" height="11" />
		</svg>
		Chart
	</button>
</div>
