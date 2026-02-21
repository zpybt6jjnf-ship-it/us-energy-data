<script lang="ts">
	interface Option {
		value: string;
		label: string;
	}

	interface Props {
		options: Option[];
		value: string;
		label?: string;
		onchange: (value: string) => void;
	}

	let { options, value, label = '', onchange }: Props = $props();
</script>

<div class="relative inline-flex items-center gap-2">
	{#if label}
		<span class="text-sm font-medium text-text-secondary">{label}</span>
	{/if}
	<div class="relative">
		<select
			class="appearance-none rounded-lg border border-border bg-surface-card pl-3 pr-8 py-1.5 text-sm font-medium text-text shadow-sm hover:border-accent/40 focus:border-accent focus:ring-2 focus:ring-accent/20 focus:outline-none transition-colors cursor-pointer"
			{value}
			onchange={(e) => onchange(e.currentTarget.value)}
		>
			{#each options as opt}
				<option value={opt.value} selected={opt.value === value}>{opt.label}</option>
			{/each}
		</select>
		<svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6l4 4 4-4"/></svg>
	</div>
</div>
