import { feature } from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const results = await Promise.allSettled([
		fetchJSON<any>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any>(fetch, '/data/generation/generation-by-state.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/capacity-national.json'),
		fetchJSON<any>(fetch, '/data/generation/carbon-intensity-national.json'),
		fetchJSON<any>(fetch, '/data/generation/capacity-changes-national.json'),
		fetchJSON<any>(fetch, '/data/generation/storage-national.json'),
		fetchJSON<any>(fetch, '/data/generation/metadata.json'),
	]);

	const national = results[0].status === 'fulfilled' ? results[0].value : [];
	const byState = results[1].status === 'fulfilled' ? results[1].value : [];
	const renewableShare = results[2].status === 'fulfilled' ? results[2].value : [];
	const topo = results[3].status === 'fulfilled' ? results[3].value : null;
	const capacity = results[4].status === 'fulfilled' ? results[4].value : [];
	const carbonIntensity = results[5].status === 'fulfilled' ? results[5].value : [];
	const capacityChanges = results[6].status === 'fulfilled' ? results[6].value : [];
	const storage = results[7].status === 'fulfilled' ? results[7].value : [];
	const metadata = results[8].status === 'fulfilled' ? results[8].value : null;

	for (let i = 0; i < results.length; i++) {
		if (results[i].status === 'rejected') {
			console.warn(`Failed to fetch generation data [${i}]:`, (results[i] as PromiseRejectedResult).reason);
		}
	}

	const topology = topo
		? feature(topo as Topology, (topo as Topology).objects.states as GeometryCollection)
		: { type: 'FeatureCollection' as const, features: [] };
	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, renewableShare, topology, capacity, carbonIntensity, capacityChanges, storage, lastUpdated };
}
