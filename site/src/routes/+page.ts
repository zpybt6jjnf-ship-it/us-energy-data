import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const results = await Promise.allSettled([
		fetchJSON<any[]>(fetch, '/data/prices/retail-prices-national.json'),
		fetchJSON<any[]>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any[]>(fetch, '/data/demand/consumption-national.json'),
	]);

	const prices = results[0].status === 'fulfilled' ? results[0].value : [];
	const generation = results[1].status === 'fulfilled' ? results[1].value : [];
	const consumption = results[2].status === 'fulfilled' ? results[2].value : [];

	if (results[0].status === 'rejected') console.warn('Failed to fetch retail prices:', results[0].reason);
	if (results[1].status === 'rejected') console.warn('Failed to fetch generation data:', results[1].reason);
	if (results[2].status === 'rejected') console.warn('Failed to fetch consumption data:', results[2].reason);

	// Latest residential price
	const latestPriceYear = prices.length > 0 ? Math.max(...prices.map((d: any) => d.year)) : 0;
	const resPrices = prices.filter(
		(d: any) => d.year === latestPriceYear && d.sector === 'Residential'
	);
	const avgResPrice = resPrices.length > 0 ? resPrices[0].price : 0;

	// Natural gas share of generation (latest year)
	const latestGenYear = generation.length > 0 ? Math.max(...generation.map((d: any) => d.year)) : 0;
	const gasShare =
		generation.find(
			(d: any) => d.year === latestGenYear && d.source === 'Natural Gas'
		)?.share ?? 0;

	// Total annual consumption (latest year, all sectors summed)
	const latestDemandYear = consumption.length > 0 ? Math.max(...consumption.map((d: any) => d.year)) : 0;
	const totalConsumption = consumption
		.filter((d: any) => d.year === latestDemandYear)
		.reduce((sum: number, d: any) => sum + d.consumption, 0);

	// Convert million kWh to trillion kWh
	const totalTWh = totalConsumption / 1_000_000;

	return {
		stats: {
			avgResPrice: `${avgResPrice.toFixed(1)}\u00a2`,
			priceLabel: latestPriceYear ? `avg. residential electricity price (${latestPriceYear})` : 'avg. residential electricity price',
			gasShare: `${Math.round(gasShare)}%`,
			gasLabel: 'of electricity from natural gas',
			totalConsumption: `${totalTWh.toFixed(1)}T kWh`,
			consumptionLabel: 'annual electricity consumption',
		},
		generationData: generation,
	};
}
