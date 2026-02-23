import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure, metadata] = await Promise.all([
		fetchJSON<any>(fetch, '/data/reliability/saidi-national.json'),
		fetchJSON<any>(fetch, '/data/reliability/saidi-by-state.json'),
		fetchJSON<any>(fetch, '/data/reliability/saidi-by-state-trend.json'),
		fetchJSON<any>(fetch, '/data/prices/retail-prices-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/market-structure.json'),
		fetchJSON<any>(fetch, '/data/reliability/metadata.json'),
	]);

	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, byStateTrend, pricesByState, topology, renewableShare, marketStructure, lastUpdated };
}
