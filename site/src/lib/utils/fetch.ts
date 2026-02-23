import { error } from '@sveltejs/kit';

export async function fetchJSON<T = unknown>(fetch: typeof globalThis.fetch, url: string): Promise<T> {
	const res = await fetch(url);
	if (!res.ok) throw error(res.status, `Failed to load ${url}: ${res.statusText}`);
	return res.json() as Promise<T>;
}
