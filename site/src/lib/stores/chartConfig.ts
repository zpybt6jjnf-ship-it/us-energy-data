import { page } from '$app/stores';
import { goto } from '$app/navigation';
import { derived } from 'svelte/store';
import type { ChartConfig } from '$types/chart';

const DEFAULTS: ChartConfig = {
	states: [],
	sector: 'all',
	metric: 'nominal',
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

/** Reset all config params to defaults */
export function resetConfig(): void {
	goto(window.location.pathname, { replaceState: true, noScroll: true });
}
