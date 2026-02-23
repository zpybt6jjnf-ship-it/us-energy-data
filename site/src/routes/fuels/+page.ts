import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, generation, trade] = await Promise.all([
		fetchJSON<any>(fetch, '/data/fuels/production-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/production-by-state.json'),
		fetchJSON<any>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/trade-national.json'),
	]);

	return { national, byState, generation, trade };
}
