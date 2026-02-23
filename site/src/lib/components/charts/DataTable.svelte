<script lang="ts">
	interface Column {
		key: string;
		label: string;
		format?: (v: unknown) => string;
	}

	interface Props {
		data: Record<string, unknown>[];
		columns?: Column[];
		unit?: string;
	}

	let { data, columns: propColumns, unit }: Props = $props();

	// Auto-detect columns from first row keys if not provided
	const columns = $derived(
		propColumns ??
			(data.length > 0
				? Object.keys(data[0]).map((key) => ({
						key,
						label: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' '),
					}))
				: [])
	);

	let sortKey = $state('');
	let sortDir = $state<'asc' | 'desc'>('asc');

	function handleSort(key: string) {
		if (sortKey === key) {
			sortDir = sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			sortKey = key;
			sortDir = 'asc';
		}
	}

	const sortedData = $derived((() => {
		if (!sortKey) return data;
		return [...data].sort((a, b) => {
			const av = a[sortKey];
			const bv = b[sortKey];
			if (av == null && bv == null) return 0;
			if (av == null) return 1;
			if (bv == null) return -1;
			const cmp = typeof av === 'number' && typeof bv === 'number'
				? av - bv
				: String(av).localeCompare(String(bv));
			return sortDir === 'asc' ? cmp : -cmp;
		});
	})());

	function formatCell(col: Column, value: unknown): string {
		if (value == null) return '—';
		if (col.format) return col.format(value);
		if (typeof value === 'number') return value.toLocaleString();
		return String(value);
	}
</script>

<div class="max-h-[400px] overflow-y-auto border border-border rounded-lg">
	<table class="w-full text-xs font-mono border-collapse">
		<thead class="sticky top-0 bg-surface-card z-10">
			<tr>
				{#each columns as col}
					<th
						class="px-3 py-2 text-left font-semibold text-text-secondary border-b border-border cursor-pointer hover:text-accent select-none whitespace-nowrap"
						onclick={() => handleSort(col.key)}
					>
						{col.label}
						{#if sortKey === col.key}
							<span class="ml-0.5">{sortDir === 'asc' ? '↑' : '↓'}</span>
						{/if}
					</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each sortedData as row, i}
				<tr class={i % 2 === 0 ? 'bg-transparent' : 'bg-surface-alt'}>
					{#each columns as col}
						<td class="px-3 py-1.5 text-text whitespace-nowrap">
							{formatCell(col, row[col.key])}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
	{#if unit}
		<div class="px-3 py-1.5 text-[10px] text-text-muted border-t border-border bg-surface-card">
			Unit: {unit}
		</div>
	{/if}
</div>
