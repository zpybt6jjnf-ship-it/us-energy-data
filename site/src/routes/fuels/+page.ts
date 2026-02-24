import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const results = await Promise.allSettled([
		fetchJSON<any>(fetch, '/data/fuels/production-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/production-by-state.json'),
		fetchJSON<any>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/trade-national.json'),
		fetchJSON<any>(fetch, '/data/fuels/metadata.json'),
	]);

	const national = results[0].status === 'fulfilled' ? results[0].value : [];
	const byState = results[1].status === 'fulfilled' ? results[1].value : [];
	const generation = results[2].status === 'fulfilled' ? results[2].value : [];
	const trade = results[3].status === 'fulfilled' ? results[3].value : [];
	const metadata = results[4].status === 'fulfilled' ? results[4].value : null;

	for (let i = 0; i < results.length; i++) {
		if (results[i].status === 'rejected') {
			console.warn(`Failed to fetch fuels data [${i}]:`, (results[i] as PromiseRejectedResult).reason);
		}
	}

	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, generation, trade, lastUpdated };
}
