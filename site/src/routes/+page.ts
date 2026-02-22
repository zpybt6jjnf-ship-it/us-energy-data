export async function load({ fetch }) {
	const [prices, generation, consumption] = await Promise.all([
		fetch('/data/prices/retail-prices-national.json').then((r) => r.json()),
		fetch('/data/generation/generation-national.json').then((r) => r.json()),
		fetch('/data/demand/consumption-national.json').then((r) => r.json()),
	]);

	// Latest residential price
	const latestPriceYear = Math.max(...prices.map((d: any) => d.year));
	const resPrices = prices.filter(
		(d: any) => d.year === latestPriceYear && d.sector === 'Residential'
	);
	const avgResPrice = resPrices.length > 0 ? resPrices[0].price : 0;

	// Natural gas share of generation (latest year)
	const latestGenYear = Math.max(...generation.map((d: any) => d.year));
	const gasShare =
		generation.find(
			(d: any) => d.year === latestGenYear && d.source === 'Natural Gas'
		)?.share ?? 0;

	// Total annual consumption (latest year, all sectors summed)
	const latestDemandYear = Math.max(...consumption.map((d: any) => d.year));
	const totalConsumption = consumption
		.filter((d: any) => d.year === latestDemandYear)
		.reduce((sum: number, d: any) => sum + d.consumption, 0);

	// Convert million kWh to trillion kWh
	const totalTWh = totalConsumption / 1_000_000;

	// Fetch sparkline data — gracefully degrade on failure
	let generationData: any[] = [];
	let priceData: any[] = [];
	let demandData: any[] = [];

	try {
		generationData = generation;
	} catch {
		generationData = [];
	}

	try {
		priceData = prices;
	} catch {
		priceData = [];
	}

	try {
		demandData = consumption;
	} catch {
		demandData = [];
	}

	return {
		stats: {
			avgResPrice: `${avgResPrice.toFixed(1)}\u00a2`,
			priceLabel: `avg. residential electricity price (${latestPriceYear})`,
			gasShare: `${Math.round(gasShare)}%`,
			gasLabel: 'of electricity from natural gas',
			totalConsumption: `${totalTWh.toFixed(1)}T kWh`,
			consumptionLabel: 'annual electricity consumption',
		},
		generationData,
		priceData,
		demandData,
	};
}
