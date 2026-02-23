import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';
import { fetchJSON } from '$utils/fetch';

export async function load({ fetch }) {
	const [national, byState, topo, renewableShare, bills, marketStructure, metadata] = await Promise.all([
		fetchJSON<any>(fetch, '/data/prices/retail-prices-national.json'),
		fetchJSON<any>(fetch, '/data/prices/retail-prices-by-state.json'),
		fetchJSON<any>(fetch, '/data/meta/us-states.json'),
		fetchJSON<any>(fetch, '/data/generation/renewable-share-by-state.json'),
		fetchJSON<any>(fetch, '/data/bills/household-bills-national.json'),
		fetchJSON<any>(fetch, '/data/meta/market-structure.json'),
		fetchJSON<any>(fetch, '/data/prices/metadata.json'),
	]);

	const topology = feature(topo as Topology, (topo as any).objects.states);
	const lastUpdated = metadata?.last_updated?.split('T')[0] ?? new Date().toISOString().split('T')[0];

	return { national, byState, topology, renewableShare, bills, marketStructure, lastUpdated };
}
