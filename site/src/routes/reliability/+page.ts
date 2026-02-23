import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure] = await Promise.all([
		fetchJSON<any>(fetch, '/data/reliability/saidi-national.json'),
		fetchJSON<any>(fetch, '/data/reliability/saidi-by-state.json'),
		fetchJSON<any>(fetch, '/data/reliability/saidi-by-state-trend.json'),
		fetchJSON<any>(fetch, '/data/prices/retail-prices-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/market-structure.json'),
	]);

	return { national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure };
}
