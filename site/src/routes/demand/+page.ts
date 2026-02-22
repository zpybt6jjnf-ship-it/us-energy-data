export async function load({ fetch }) {
	const [national, byState, perCapita] = await Promise.all([
		fetch('/data/demand/consumption-national.json').then((r) => r.json()),
		fetch('/data/demand/consumption-by-state.json').then((r) => r.json()),
		fetch('/data/demand/per-capita-by-state.json').then((r) => r.json()),
	]);

	return { national, byState, perCapita };
}
