import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const results = await Promise.allSettled([
		fetchJSON<any>(fetch, '/data/demand/consumption-national.json'),
		fetchJSON<any>(fetch, '/data/demand/consumption-by-state.json'),
		fetchJSON<any>(fetch, '/data/demand/per-capita-by-state.json'),
		fetchJSON<any>(fetch, '/data/demand/metadata.json'),
	]);

	const national = results[0].status === 'fulfilled' ? results[0].value : [];
	const byState = results[1].status === 'fulfilled' ? results[1].value : [];
	const perCapita = results[2].status === 'fulfilled' ? results[2].value : [];
	const metadata = results[3].status === 'fulfilled' ? results[3].value : null;

	for (let i = 0; i < results.length; i++) {
		if (results[i].status === 'rejected') {
			console.warn(`Failed to fetch demand data [${i}]:`, (results[i] as PromiseRejectedResult).reason);
		}
	}

	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, perCapita, lastUpdated };
}
