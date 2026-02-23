import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, generation, trade, metadata] = await Promise.all([
		fetchJSON<any>(fetch, '/data/fuels/production-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/production-by-state.json'),
		fetchJSON<any>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/trade-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/metadata.json'),
	]);

	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, generation, trade, lastUpdated };
}
