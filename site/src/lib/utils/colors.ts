export const CHART_COLORS = [
	'#2166ac', // blue
	'#e86c3a', // orange
	'#1b9e77', // teal
	'#984ea3', // purple
	'#e7a02f', // gold
	'#a6611a', // brown
	'#666666', // gray
	'#e31a1c', // red
] as const;

export const ENERGY_SOURCE_COLORS: Record<string, string> = {
	coal: '#4a4a4a',
	'natural gas': '#e86c3a',
	nuclear: '#984ea3',
	wind: '#2166ac',
	solar: '#e7a02f',
	hydro: '#1b9e77',
	petroleum: '#a6611a',
	biomass: '#66a61e',
	geothermal: '#e31a1c',
	other: '#999999',
};

export function getSeriesColor(index: number): string {
	return CHART_COLORS[index % CHART_COLORS.length];
}
