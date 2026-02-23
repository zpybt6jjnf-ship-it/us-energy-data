<script lang="ts">
	interface Props {
		min: number;
		max: number;
		value: number;
		onchange: (year: number) => void;
	}

	let { min, max, value, onchange }: Props = $props();
	let playing = $state(false);
	let intervalId: ReturnType<typeof setInterval> | null = $state(null);

	function togglePlay() {
		if (playing) {
			stop();
		} else {
			play();
		}
	}

	function play() {
		playing = true;
		// If at the end, restart from beginning
		if (value >= max) {
			onchange(min);
		}
		intervalId = setInterval(() => {
			const next = value + 1;
			if (next > max) {
				stop();
			} else {
				onchange(next);
			}
		}, 800);
	}

	function stop() {
		playing = false;
		if (intervalId !== null) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		onchange(Number(target.value));
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
			e.preventDefault();
			if (value < max) onchange(value + 1);
		} else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
			e.preventDefault();
			if (value > min) onchange(value - 1);
		}
	}

	// Clean up on unmount
	$effect(() => {
		return () => {
			if (intervalId !== null) clearInterval(intervalId);
		};
	});
</script>

<div class="flex items-center gap-2">
	<button
		type="button"
		onclick={togglePlay}
		aria-label={playing ? 'Pause animation' : 'Play animation'}
		class="flex h-6 w-6 items-center justify-center rounded-full border border-border bg-surface-card text-text-secondary hover:border-accent hover:text-accent transition-colors cursor-pointer"
	>
		{#if playing}
			<svg class="h-3 w-3" viewBox="0 0 12 12" fill="currentColor">
				<rect x="2" y="2" width="3" height="8" rx="0.5" />
				<rect x="7" y="2" width="3" height="8" rx="0.5" />
			</svg>
		{:else}
			<svg class="h-3 w-3" viewBox="0 0 12 12" fill="currentColor">
				<polygon points="3,1 10,6 3,11" />
			</svg>
		{/if}
	</button>

	<input
		type="range"
		{min}
		{max}
		{value}
		oninput={handleInput}
		onkeydown={handleKeydown}
		class="year-slider flex-1 h-1.5 cursor-pointer accent-accent"
		aria-label="Select year"
		aria-valuemin={min}
		aria-valuemax={max}
		aria-valuenow={value}
	/>

	<span class="text-sm font-mono font-semibold text-text tabular-nums min-w-[3ch]">{value}</span>
</div>

<style>
	.year-slider {
		-webkit-appearance: none;
		appearance: none;
		background: var(--color-border);
		border-radius: 9999px;
		outline: none;
	}
	.year-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: var(--color-accent);
		border: 2px solid var(--color-surface-card);
		box-shadow: 0 1px 3px rgba(0,0,0,0.15);
		cursor: pointer;
	}
	.year-slider::-moz-range-thumb {
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: var(--color-accent);
		border: 2px solid var(--color-surface-card);
		box-shadow: 0 1px 3px rgba(0,0,0,0.15);
		cursor: pointer;
	}
	.year-slider:focus-visible::-webkit-slider-thumb {
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-accent) 30%, transparent);
	}
</style>
