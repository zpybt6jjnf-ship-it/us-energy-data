export const CHART_COLORS = [
	'#286EA8', // steel blue
	'#C98600', // amber
	'#18A865', // green
	'#7C5CC4', // purple
	'#D14040', // red
	'#1DA876', // teal
	'#6B7280', // slate
	'#D4660A', // orange
] as const;

/** CSS-variable-based chart colors — auto-adapt to dark mode */
export const CHART_COLORS_CSS = [
	'var(--color-chart-1, #286EA8)',
	'var(--color-chart-2, #C98600)',
	'var(--color-chart-3, #18A865)',
	'var(--color-chart-4, #7C5CC4)',
	'var(--color-chart-5, #D14040)',
	'var(--color-chart-6, #1DA876)',
	'var(--color-chart-7, #6B7280)',
	'var(--color-chart-8, #D4660A)',
] as const;

export const ENERGY_SOURCE_COLORS: Record<string, string> = {
	coal: 'var(--color-fuel-coal, #6B7280)',
	'natural gas': 'var(--color-fuel-gas, #C98600)',
	nuclear: 'var(--color-fuel-nuclear, #7C5CC4)',
	wind: 'var(--color-fuel-wind, #286EA8)',
	solar: 'var(--color-fuel-solar, #C99200)',
	hydro: 'var(--color-fuel-hydro, #18A865)',
	petroleum: 'var(--color-fuel-petroleum, #D4660A)',
	biomass: 'var(--color-fuel-biomass, #1DA876)',
	geothermal: 'var(--color-fuel-geothermal, #D14040)',
	other: 'var(--color-fuel-other, #6B7280)',
};

export function getSeriesColor(index: number): string {
	return CHART_COLORS_CSS[index % CHART_COLORS_CSS.length];
}

export const FUEL_COLORS: Record<string, string> = {
	Coal: 'var(--color-fuel-coal, #6B7280)',
	'Natural Gas': 'var(--color-fuel-gas, #C98600)',
	'Crude Oil': 'var(--color-fuel-petroleum, #D4660A)',
};

export const FUEL_GEN_COLORS: Record<string, string> = {
	Coal: 'var(--color-fuel-coal, #6B7280)',
	'Natural Gas': 'var(--color-fuel-gas, #C98600)',
	Petroleum: 'var(--color-fuel-petroleum, #D4660A)',
};

export const TRADE_COLORS: Record<string, string> = {
	Imports: 'var(--color-chart-1, #286EA8)',
	Exports: 'var(--color-chart-8, #D4660A)',
	'Net Imports': 'var(--color-chart-7, #6B7280)',
};

export const CATEGORY_COLORS: Record<string, string> = {
	Fossil: 'var(--color-chart-7, #6B7280)',
	Nuclear: 'var(--color-chart-4, #7C5CC4)',
	Renewable: 'var(--color-chart-3, #18A865)',
};

export const SEMANTIC_COLORS = { positive: 'var(--color-highlight, #18A865)', negative: 'var(--color-chart-5, #D14040)' } as const;

export const BILLS_COLORS = { nominal: 'var(--color-chart-2, #C98600)', real: 'var(--color-chart-1, #286EA8)' } as const;

export const LOGO_GRADIENT = ['#2a9d8f', '#e9c46a', '#e76f51'] as const;

export const MAP_LABEL_COLORS = { dark: 'var(--color-text, #1C1917)', light: 'var(--color-surface, #FFFFFF)' } as const;

export const MAP_DEFAULT_RANGE = ['#F3F1EC', '#286EA8'] as const;

export const EXPORT_FALLBACKS = { text: '#1C1917', textSecondary: '#57534E', surface: '#FAF9F6' } as const;

export const REFERENCE_COLOR = 'var(--color-text-muted, #999)' as const;

export const STORAGE_COLOR = 'var(--color-chart-4, #7C5CC4)' as const;

export const CARBON_INTENSITY_COLOR = 'var(--color-chart-7, #6B7280)' as const;

export const STATE_BAR_COLOR = 'var(--color-chart-8, #D4660A)' as const;
