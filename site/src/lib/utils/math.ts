/**
 * Compute a centered moving average over a time series.
 * NaN/null values are skipped. If the window has fewer than half valid points, returns NaN.
 */
export function movingAverage(
	values: { date: number; value: number }[],
	windowSize: number
): { date: number; value: number }[] {
	const half = Math.floor(windowSize / 2);
	return values.map((pt, i) => {
		const start = Math.max(0, i - half);
		const end = Math.min(values.length - 1, i + half);
		let sum = 0;
		let count = 0;
		for (let j = start; j <= end; j++) {
			const v = values[j].value;
			if (v != null && Number.isFinite(v)) {
				sum += v;
				count++;
			}
		}
		return {
			date: pt.date,
			value: count >= Math.ceil(windowSize / 2) ? sum / count : NaN,
		};
	}).filter((pt) => Number.isFinite(pt.value));
}

/**
 * Simple linear regression on a time series.
 * Returns slope, intercept, and R² coefficient of determination.
 */
export function linearRegression(
	values: { date: number; value: number }[]
): { slope: number; intercept: number; r2: number } {
	const n = values.length;
	if (n < 2) return { slope: 0, intercept: values[0]?.value ?? 0, r2: 0 };

	let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;
	for (const { date, value } of values) {
		sumX += date;
		sumY += value;
		sumXY += date * value;
		sumX2 += date * date;
		sumY2 += value * value;
	}

	const denom = n * sumX2 - sumX * sumX;
	if (denom === 0) return { slope: 0, intercept: sumY / n, r2: 0 };

	const slope = (n * sumXY - sumX * sumY) / denom;
	const intercept = (sumY - slope * sumX) / n;

	const ssRes = values.reduce((s, { date, value }) => {
		const predicted = slope * date + intercept;
		return s + (value - predicted) ** 2;
	}, 0);
	const meanY = sumY / n;
	const ssTot = values.reduce((s, { value }) => s + (value - meanY) ** 2, 0);
	const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0;

	return { slope, intercept, r2 };
}
