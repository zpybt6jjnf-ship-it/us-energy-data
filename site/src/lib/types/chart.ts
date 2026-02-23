export interface DataPoint {
	date: number;
	value: number;
}

export interface DataSeries {
	name: string;
	values: DataPoint[];
	color?: string;
}

export interface ChartConfig {
	states: string[];
	sector: string;
	metric: string;
	med: string;
	fuel: string;
	startYear: number;
	endYear: number;
}

export interface ChartMeta {
	title: string;
	subtitle?: string;
	source: string;
	sourceUrl: string;
	unit: string;
	lastUpdated: string;
	description?: string;
	caveats?: string;
}

export interface Margin {
	top: number;
	right: number;
	bottom: number;
	left: number;
}

export interface TooltipData {
	x: number;
	y: number;
	header?: string;
	subtitle?: string;
	items: { label: string; value: string; color: string }[];
}
