import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';

export async function load({ fetch }) {
	const [national, byState, topo] = await Promise.all([
		fetch('/data/prices/retail-prices-national.json').then((r) => r.json()),
		fetch('/data/prices/retail-prices-by-state.json').then((r) => r.json()),
		fetch('/data/meta/us-states.json').then((r) => r.json()),
	]);

	const topology = feature(topo as Topology, (topo as any).objects.states);

	return { national, byState, topology };
}
