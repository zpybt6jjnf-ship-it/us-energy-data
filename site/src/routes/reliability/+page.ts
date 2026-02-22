export async function load({ fetch }) {
	const [national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure] = await Promise.all([
		fetch('/data/reliability/saidi-national.json').then((r) => r.json()),
		fetch('/data/reliability/saidi-by-state.json').then((r) => r.json()),
		fetch('/data/reliability/saidi-by-state-trend.json').then((r) => r.json()),
		fetch('/data/prices/retail-prices-by-state.json').then((r) => r.json()),
		fetch('/data/meta/us-states.json').then((r) => r.json()),
		fetch('/data/generation/renewable-share-by-state.json').then((r) => r.json()),
		fetch('/data/meta/market-structure.json').then((r) => r.json()),
	]);

	return { national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure };
}
