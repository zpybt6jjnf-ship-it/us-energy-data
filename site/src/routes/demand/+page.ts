import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, perCapita] = await Promise.all([
		fetchJSON<any>(fetch, '/data/demand/consumption-national.json'),
		fetchJSON<any>(fetch, '/data/demand/consumption-by-state.json'),
		fetchJSON<any>(fetch, '/data/demand/per-capita-by-state.json'),
	]);

	return { national, byState, perCapita };
}
