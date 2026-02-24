import { feature } from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const results = await Promise.allSettled([
		fetchJSON<any>(fetch, '/data/prices/retail-prices-national.json'),
		fetchJSON<any>(fetch, '/data/prices/retail-prices-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/bills/household-bills-national.json'),
		fetchJSON<any>(fetch, '/data/meta/market-structure.json'),
		fetchJSON<any>(fetch, '/data/prices/metadata.json'),
	]);

	const national = results[0].status === 'fulfilled' ? results[0].value : [];
	const byState = results[1].status === 'fulfilled' ? results[1].value : [];
	const topo = results[2].status === 'fulfilled' ? results[2].value : null;
	const renewableShare = results[3].status === 'fulfilled' ? results[3].value : [];
	const bills = results[4].status === 'fulfilled' ? results[4].value : [];
	const marketStructure = results[5].status === 'fulfilled' ? results[5].value : [];
	const metadata = results[6].status === 'fulfilled' ? results[6].value : null;

	for (let i = 0; i < results.length; i++) {
		if (results[i].status === 'rejected') {
			console.warn(`Failed to fetch prices data [${i}]:`, (results[i] as PromiseRejectedResult).reason);
		}
	}

	const topology = topo
		? feature(topo as Topology, (topo as Topology).objects.states as GeometryCollection)
		: { type: 'FeatureCollection' as const, features: [] };
	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, topology, renewableShare, bills, marketStructure, lastUpdated };
}
