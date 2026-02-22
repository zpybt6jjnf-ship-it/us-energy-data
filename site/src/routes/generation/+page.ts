import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';

export async function load({ fetch }) {
	const [national, byState, renewableShare, topo, capacity, carbonIntensity, capacityChanges, storage] = await Promise.all([
		fetch('/data/generation/generation-national.json').then((r) => r.json()),
		fetch('/data/generation/generation-by-state.json').then((r) => r.json()),
		fetch('/data/generation/renewable-share-by-state.json').then((r) => r.json()),
		fetch('/data/meta/us-states.json').then((r) => r.json()),
		fetch('/data/generation/capacity-national.json').then((r) => r.json()),
		fetch('/data/generation/carbon-intensity-national.json').then((r) => r.json()),
		fetch('/data/generation/capacity-changes-national.json').then((r) => r.json()),
		fetch('/data/generation/storage-national.json').then((r) => r.json()),
	]);

	const topology = feature(topo as Topology, (topo as any).objects.states);

	return { national, byState, renewableShare, topology, capacity, carbonIntensity, capacityChanges, storage };
}
