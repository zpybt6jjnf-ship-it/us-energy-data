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

export const ENERGY_SOURCE_COLORS: Record<string, string> = {
	coal: '#6B7280',
	'natural gas': '#C98600',
	nuclear: '#7C5CC4',
	wind: '#286EA8',
	solar: '#E6A817',
	hydro: '#18A865',
	petroleum: '#D4660A',
	biomass: '#1DA876',
	geothermal: '#D14040',
	other: '#6B7280',
};

export function getSeriesColor(index: number): string {
	return CHART_COLORS[index % CHART_COLORS.length];
}

export const FUEL_COLORS: Record<string, string> = {
	Coal: '#6B7280',
	'Natural Gas': '#C98600',
	'Crude Oil': '#D4660A',
};

export const FUEL_GEN_COLORS: Record<string, string> = {
	Coal: '#6B7280',
	'Natural Gas': '#C98600',
	Petroleum: '#D4660A',
};

export const TRADE_COLORS: Record<string, string> = {
	Imports: '#D14040',
	Exports: '#286EA8',
	'Net Imports': '#18A865',
};

export const CATEGORY_COLORS: Record<string, string> = {
	Fossil: '#6B7280',
	Nuclear: '#7C5CC4',
	Renewable: '#18A865',
};

export const SEMANTIC_COLORS = { positive: '#18A865', negative: '#D14040' } as const;

export const BILLS_COLORS = { nominal: '#C98600', real: '#286EA8' } as const;

export const LOGO_GRADIENT = ['#2a9d8f', '#e9c46a', '#e76f51'] as const;

export const MAP_LABEL_COLORS = { dark: '#1C1917', light: '#FFFFFF' } as const;

export const MAP_DEFAULT_RANGE = ['#F3F1EC', '#286EA8'] as const;

export const EXPORT_FALLBACKS = { text: '#1C1917', textSecondary: '#57534E', surface: '#FAF9F6' } as const;

export const REFERENCE_COLOR = '#999' as const;

export const STORAGE_COLOR = '#7C5CC4' as const;

export const CARBON_INTENSITY_COLOR = '#6B7280' as const;

export const STATE_BAR_COLOR = '#D4660A' as const;
