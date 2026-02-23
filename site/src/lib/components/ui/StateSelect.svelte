<script lang="ts">
	import { FIPS_TO_ABBR } from '$utils/states';

	interface Props {
		selected: string[];
		onchange: (states: string[]) => void;
		label?: string;
		maxSelections?: number;
		compact?: boolean;
	}

	let { selected, onchange, label = 'Compare states', maxSelections = 6, compact = false }: Props = $props();

	const atLimit = $derived(selected.length >= maxSelections);

	let open = $state(false);
	let query = $state('');
	let inputEl: HTMLInputElement | undefined = $state();

	// All state abbreviations sorted alphabetically
	const allStates = Object.values(FIPS_TO_ABBR).sort();

	const filtered = $derived(
		query.length === 0
			? allStates
			: allStates.filter((abbr) => abbr.toLowerCase().includes(query.toLowerCase()))
	);

	function toggle(abbr: string) {
		if (selected.includes(abbr)) {
			onchange(selected.filter((s) => s !== abbr));
		} else if (!atLimit) {
			onchange([...selected, abbr]);
		}
		query = '';
	}

	function remove(abbr: string) {
		onchange(selected.filter((s) => s !== abbr));
	}

	function clearAll() {
		onchange([]);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			open = false;
			query = '';
		} else if (event.key === 'Backspace' && query === '' && selected.length > 0) {
			onchange(selected.slice(0, -1));
		}
	}

	function handleBlur(event: FocusEvent) {
		const related = event.relatedTarget as HTMLElement | null;
		if (related?.closest('.state-select-dropdown')) return;
		setTimeout(() => { open = false; query = ''; }, 150);
	}

	const quickAddStates = ['TX', 'CA', 'NY', 'FL', 'IL'];

	const interestingStates = ['TX', 'CA', 'NY', 'WA', 'WY', 'HI', 'LA', 'IA', 'VT', 'ME', 'ND', 'WV'];

	function surpriseMe() {
		const shuffled = [...interestingStates].sort(() => Math.random() - 0.5);
		onchange(shuffled.slice(0, 3));
	}
</script>

<div class="relative inline-flex flex-col gap-1.5">
	{#if label}
		<span class="text-sm font-medium text-text-secondary">{label}</span>
	{/if}

	<div
		class="state-select-dropdown flex min-h-[34px] flex-wrap items-center gap-1 rounded-lg border border-border bg-surface-card px-2 py-1 shadow-sm transition-colors focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20"
		role="combobox"
		aria-expanded={open}
		aria-controls="state-select-listbox"
		aria-haspopup="listbox"
	>
		<!-- Selected tags -->
		{#each selected as abbr}
			<span class="inline-flex items-center gap-0.5 rounded-md bg-accent/15 px-1.5 py-0.5 text-xs font-semibold text-accent">
				{abbr}
				<button
					type="button"
					class="ml-0.5 text-accent/60 hover:text-accent cursor-pointer"
					onclick={() => remove(abbr)}
					aria-label="Remove {abbr}"
				>
					<svg class="h-3 w-3" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3l6 6M9 3l-6 6"/></svg>
				</button>
			</span>
		{/each}

		<!-- Search input -->
		<input
			bind:this={inputEl}
			type="text"
			class="min-w-[3rem] flex-1 border-0 bg-transparent px-1 py-0.5 text-sm text-text outline-none placeholder:text-text-muted"
			placeholder={selected.length === 0 ? (compact ? 'Add state...' : 'Add states...') : atLimit ? `Max ${maxSelections} states` : ''}
			bind:value={query}
			onfocus={() => open = true}
			onblur={handleBlur}
			onkeydown={handleKeydown}
			autocomplete="off"
			spellcheck="false"
		/>

		{#if selected.length > 0}
			<button
				type="button"
				class="ml-1 text-text-muted hover:text-text cursor-pointer"
				onclick={clearAll}
				aria-label="Clear all"
			>
				<svg class="h-3.5 w-3.5" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3l8 8M11 3l-8 8"/></svg>
			</button>
		{/if}
	</div>

	<!-- Quick-add chips -->
	{#if !compact && selected.length === 0 && !open}
		<div class="flex flex-wrap items-center gap-1.5 mt-1">
			{#each quickAddStates as abbr}
				<button
					type="button"
					class="rounded-full border border-border px-2.5 py-0.5 text-xs font-medium text-text-secondary hover:border-accent hover:text-accent transition-colors cursor-pointer"
					onclick={() => toggle(abbr)}
				>
					{abbr}
				</button>
			{/each}
			<button
				type="button"
				class="rounded-full border border-dashed border-border px-2.5 py-0.5 text-xs font-medium text-text-muted hover:border-accent hover:text-accent transition-colors cursor-pointer"
				onclick={surpriseMe}
			>
				Surprise me
			</button>
		</div>
	{/if}

	<!-- Dropdown -->
	{#if open}
		<div id="state-select-listbox" role="listbox" class="state-select-dropdown absolute top-full z-50 mt-1 max-h-48 w-full overflow-auto rounded-lg border border-border bg-surface-card shadow-lg">
			{#if filtered.length === 0}
				<div class="px-3 py-2 text-sm text-text-muted">No states found</div>
			{:else}
				{#each filtered as abbr}
					<button
						type="button"
						class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-text hover:bg-surface-alt transition-colors cursor-pointer text-left"
						onmousedown={(e) => { e.preventDefault(); toggle(abbr); }}
					>
						<span class="inline-flex h-4 w-4 items-center justify-center rounded border {selected.includes(abbr) ? 'border-accent bg-accent' : 'border-border'}">
							{#if selected.includes(abbr)}
								<svg class="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="2 6 5 9 10 3"/></svg>
							{/if}
						</span>
						<span class="font-medium">{abbr}</span>
					</button>
				{/each}
			{/if}
		</div>
	{/if}
</div>
