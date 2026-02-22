import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';

export async function load({ fetch }) {
	const [national, byState, topo, renewableShare, bills] = await Promise.all([
		fetch('/data/prices/retail-prices-national.json').then((r) => r.json()),
		fetch('/data/prices/retail-prices-by-state.json').then((r) => r.json()),
		fetch('/data/meta/us-states.json').then((r) => r.json()),
		fetch('/data/generation/renewable-share-by-state.json').then((r) => r.json()),
		fetch('/data/bills/household-bills-national.json').then((r) => r.json()),
	]);

	const topology = feature(topo as Topology, (topo as any).objects.states);

	return { national, byState, topology, renewableShare, bills };
}
