export async function load({ fetch }) {
	const [national, byState, generation, trade] = await Promise.all([
		fetch('/data/fuels/production-national.json').then((r) => r.json()),
		fetch('/data/fuels/production-by-state.json').then((r) => r.json()),
		fetch('/data/generation/generation-national.json').then((r) => r.json()),
		fetch('/data/fuels/trade-national.json').then((r) => r.json()),
	]);

	return { national, byState, generation, trade };
}
