export const CHART_COLORS = [
	'#5B8DEF', // steel blue
	'#FF9500', // hot amber
	'#00E68A', // vivid green
	'#C084FC', // purple
	'#FBBF24', // gold
	'#F87171', // coral red
	'#8892A4', // slate
	'#FB923C', // orange
] as const;

export const ENERGY_SOURCE_COLORS: Record<string, string> = {
	coal: '#6B7280',
	'natural gas': '#FF9500',
	nuclear: '#C084FC',
	wind: '#5B8DEF',
	solar: '#FBBF24',
	hydro: '#00E68A',
	petroleum: '#FB923C',
	biomass: '#84CC16',
	geothermal: '#F87171',
	other: '#8892A4',
};

export function getSeriesColor(index: number): string {
	return CHART_COLORS[index % CHART_COLORS.length];
}
