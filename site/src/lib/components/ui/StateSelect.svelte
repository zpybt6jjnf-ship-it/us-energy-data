<script lang="ts">
	import { FIPS_TO_ABBR } from '$utils/states';
	import { browser } from '$app/environment';

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
	let highlightedIndex = $state(-1);

	// Reset highlight when filtered list changes or dropdown closes
	$effect(() => {
		filtered; // track dependency
		highlightedIndex = -1;
	});
	$effect(() => {
		if (!open) highlightedIndex = -1;
	});

	// Scroll highlighted item into view
	$effect(() => {
		if (highlightedIndex >= 0 && open) {
			const el = document.getElementById(`state-option-${highlightedIndex}`);
			el?.scrollIntoView({ block: 'nearest' });
		}
	});

	// All state abbreviations sorted alphabetically
	const allStates = Object.values(FIPS_TO_ABBR).sort();

	const STATE_GROUPS: Record<string, string[]> = {
		'Top 5 by population': ['CA', 'TX', 'FL', 'NY', 'PA'],
		'Southeast': ['FL', 'GA', 'NC', 'SC', 'VA', 'TN', 'AL'],
		'Midwest': ['IL', 'OH', 'MI', 'IN', 'WI', 'MN', 'IA', 'MO'],
		'West Coast': ['CA', 'OR', 'WA'],
		'Northeast': ['NY', 'NJ', 'PA', 'MA', 'CT'],
	};

	const RECENT_KEY = 'stateselect-recent';

	// Load recent selections from localStorage
	let recentSelections = $state<string[][]>(
		browser ? (() => {
			try {
				const raw = localStorage.getItem(RECENT_KEY);
				return raw ? JSON.parse(raw) : [];
			} catch { return []; }
		})() : []
	);

	// Save to recents when selection changes (debounced by tracking previous)
	let prevSelected: string[] = [];
	$effect(() => {
		if (!browser) return;
		if (selected.length > 0 && JSON.stringify(selected) !== JSON.stringify(prevSelected)) {
			prevSelected = [...selected];
			const key = [...selected].sort().join(',');
			const existing = recentSelections.filter(r => [...r].sort().join(',') !== key);
			recentSelections = [[...selected], ...existing].slice(0, 3);
			try { localStorage.setItem(RECENT_KEY, JSON.stringify(recentSelections)); } catch {}
		}
	});

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

	function selectGroup(states: string[]) {
		const toAdd = states.filter(s => !selected.includes(s));
		const available = maxSelections - selected.length;
		onchange([...selected, ...toAdd.slice(0, available)]);
	}

	function applyRecent(combo: string[]) {
		onchange(combo.slice(0, maxSelections));
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
		} else if (event.key === 'ArrowDown') {
			event.preventDefault();
			if (!open) { open = true; return; }
			highlightedIndex = filtered.length > 0
				? (highlightedIndex + 1) % filtered.length
				: -1;
		} else if (event.key === 'ArrowUp') {
			event.preventDefault();
			if (!open) { open = true; return; }
			highlightedIndex = filtered.length > 0
				? (highlightedIndex - 1 + filtered.length) % filtered.length
				: -1;
		} else if (event.key === 'Enter') {
			event.preventDefault();
			if (open && highlightedIndex >= 0 && highlightedIndex < filtered.length) {
				toggle(filtered[highlightedIndex]);
			}
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

	const showGroups = $derived(query.length === 0 && open);
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
			aria-activedescendant={open && highlightedIndex >= 0 ? `state-option-${highlightedIndex}` : undefined}
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
		<div id="state-select-listbox" role="listbox" class="state-select-dropdown absolute top-full z-50 mt-1 max-h-64 w-full overflow-auto rounded-lg border border-border bg-surface-card shadow-lg min-w-[220px]">
			{#if showGroups}
				<!-- Recent selections -->
				{#if recentSelections.length > 0}
					<div class="px-3 pt-2 pb-1">
						<span class="text-[10px] uppercase tracking-wider font-semibold text-text-muted">Recent</span>
					</div>
					{#each recentSelections as combo}
						<button
							type="button"
							class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-text hover:bg-surface-alt transition-colors cursor-pointer text-left"
							onmousedown={(e) => { e.preventDefault(); applyRecent(combo); }}
						>
							<span class="text-xs text-text-secondary">{combo.join(', ')}</span>
						</button>
					{/each}
				{/if}

				<!-- Region groups -->
				{#each Object.entries(STATE_GROUPS) as [groupName, groupStates]}
					<div class="px-3 pt-2 pb-1">
						<span class="text-[10px] uppercase tracking-wider font-semibold text-text-muted">{groupName}</span>
					</div>
					<button
						type="button"
						class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-text hover:bg-surface-alt transition-colors cursor-pointer text-left"
						onmousedown={(e) => { e.preventDefault(); selectGroup(groupStates); }}
					>
						<span class="text-xs text-accent font-medium">Select all ({groupStates.length})</span>
						<span class="text-[10px] text-text-muted ml-auto">{groupStates.join(', ')}</span>
					</button>
				{/each}

				<div class="px-3 pt-2 pb-1 border-t border-border mt-1">
					<span class="text-[10px] uppercase tracking-wider font-semibold text-text-muted">All states</span>
				</div>
			{/if}

			{#if filtered.length === 0}
				<div class="px-3 py-2 text-sm text-text-muted">No states found</div>
			{:else}
				{#each filtered as abbr, i}
					<button
						type="button"
						id="state-option-{i}"
						role="option"
						aria-selected={selected.includes(abbr)}
						class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-text hover:bg-surface-alt transition-colors cursor-pointer text-left {highlightedIndex === i ? 'bg-surface-alt ring-1 ring-inset ring-accent/30' : ''}"
						onmousedown={(e) => { e.preventDefault(); toggle(abbr); }}
						onmouseenter={() => { highlightedIndex = i; }}
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
