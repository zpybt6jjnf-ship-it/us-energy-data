import { format } from 'd3-format';

const siFormat = format('.3s');
const commaFormat = format(',');
const decimalFormat = format(',.1f');
const percentFormat = format('.1%');

export function formatNumber(value: number, unit?: string): string {
	if (unit === '%' || unit === 'percent') {
		return percentFormat(value / 100);
	}
	if (Math.abs(value) >= 1_000_000) {
		return siFormat(value);
	}
	if (Math.abs(value) >= 1_000) {
		return commaFormat(Math.round(value));
	}
	if (Number.isInteger(value)) {
		return commaFormat(value);
	}
	return decimalFormat(value);
}

/** Compact SI format for axis labels (e.g., 5M, 800M, 1.2B) */
export function formatCompact(value: number): string {
	const abs = Math.abs(value);
	if (abs >= 1_000_000_000) return format('.1f')(value / 1_000_000_000) + 'B';
	if (abs >= 1_000_000) return format('.0f')(value / 1_000_000) + 'M';
	if (abs >= 1_000) return format('.0f')(value / 1_000) + 'K';
	return format(',.0f')(value);
}

export function formatCurrency(value: number): string {
	return `$${decimalFormat(value)}`;
}

export function formatYear(year: number): string {
	return String(year);
}
