export interface StateInfo {
	code: string;
	name: string;
	region: string;
	fips: string;
}

export interface SectorInfo {
	id: string;
	name: string;
	description: string;
}

export interface PriceRecord {
	state: string;
	sector: string;
	year: number;
	price: number;
}

export interface DemandRecord {
	state: string;
	sector: string;
	year: number;
	consumption: number;
	perCapita?: number;
}

export interface GenerationRecord {
	state: string;
	source: string;
	year: number;
	generation: number;
	capacity?: number;
}

export interface FuelRecord {
	state: string;
	fuel: string;
	year: number;
	production: number;
}

export interface ReliabilityRecord {
	state: string;
	year: number;
	saidi: number;
	saifi?: number;
}
