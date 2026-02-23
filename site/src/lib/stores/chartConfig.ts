import { page } from '$app/stores';
import { goto } from '$app/navigation';
import { derived } from 'svelte/store';
import type { ChartConfig } from '$types/chart';

const DEFAULTS: ChartConfig = {
	states: [],
	sector: 'all',
	metric: 'nominal',
	med: 'with_med',
	fuel: 'all',
	startYear: 2001,
	endYear: 2024,
};

/** Derived store that reads chart config from URL search params */
export const chartConfig = derived(page, ($page) => {
	const params = $page.url.searchParams;

	return {
		states: params.get('state')?.split(',').filter(Boolean) ?? DEFAULTS.states,
		sector: params.get('sector') ?? DEFAULTS.sector,
		metric: params.get('metric') ?? DEFAULTS.metric,
		med: params.get('med') ?? DEFAULTS.med,
		fuel: params.get('fuel') ?? DEFAULTS.fuel,
		startYear: Number(params.get('start')) || DEFAULTS.startYear,
		endYear: Number(params.get('end')) || DEFAULTS.endYear,
	} satisfies ChartConfig;
});

/** Update a single config parameter in the URL */
export function updateConfig(key: string, value: string | string[] | number): void {
	const url = new URL(window.location.href);

	if (Array.isArray(value)) {
		if (value.length === 0) {
			url.searchParams.delete(key);
		} else {
			url.searchParams.set(key, value.join(','));
		}
	} else {
		const defaultVal = DEFAULTS[key as keyof ChartConfig];
		if (String(value) === String(defaultVal)) {
			url.searchParams.delete(key);
		} else {
			url.searchParams.set(key, String(value));
		}
	}

	goto(url.pathname + url.search, { replaceState: true, noScroll: true });
}

/** Toggle a state abbreviation in/out of the selected states list */
export function toggleState(abbr: string): void {
	const url = new URL(window.location.href);
	const current = url.searchParams.get('state')?.split(',').filter(Boolean) ?? [];
	const idx = current.indexOf(abbr);
	if (idx >= 0) {
		current.splice(idx, 1);
	} else {
		current.push(abbr);
	}
	if (current.length === 0) {
		url.searchParams.delete('state');
	} else {
		url.searchParams.set('state', current.join(','));
	}
	goto(url.pathname + url.search, { replaceState: true, noScroll: true });
}

/** Check if any filter deviates from defaults */
export function hasActiveFilters(config: ChartConfig): boolean {
	return (
		config.states.length > 0 ||
		config.sector !== DEFAULTS.sector ||
		config.metric !== DEFAULTS.metric ||
		config.med !== DEFAULTS.med ||
		config.fuel !== DEFAULTS.fuel ||
		config.startYear !== DEFAULTS.startYear ||
		config.endYear !== DEFAULTS.endYear
	);
}

/** Reset all config params to defaults */
export function resetConfig(): void {
	goto(window.location.pathname, { replaceState: true, noScroll: true });
}
