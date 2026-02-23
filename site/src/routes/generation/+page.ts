import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';
import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, renewableShare, topo, capacity, carbonIntensity, capacityChanges, storage] = await Promise.all([
		fetchJSON<any>(fetch, '/data/generation/generation-national.json'),
		fetchJSON<any>(fetch, '/data/generation/generation-by-state.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/capacity-national.json'),
		fetchJSON<any>(fetch, '/data/generation/carbon-intensity-national.json'),
		fetchJSON<any>(fetch, '/data/generation/capacity-changes-national.json'),
		fetchJSON<any>(fetch, '/data/generation/storage-national.json'),
	]);

	const topology = feature(topo as Topology, (topo as any).objects.states);

	return { national, byState, renewableShare, topology, capacity, carbonIntensity, capacityChanges, storage };
}
