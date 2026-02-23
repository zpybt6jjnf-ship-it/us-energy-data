import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';
import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, renewableShare, topo, capacity, carbonIntensity, capacityChanges, storage, metadata] = await Promise.all([
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

	const topology = feature(topo as Topology, (topo as any).objects.states);
	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, renewableShare, topology, capacity, carbonIntensity, capacityChanges, storage, lastUpdated };
}
