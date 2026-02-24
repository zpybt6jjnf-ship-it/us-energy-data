import { EXPORT_FALLBACKS } from './colors';

export function downloadCSV(data: Record<string, unknown>[], filename: string, meta?: { source?: string; unit?: string }): void {
	if (data.length === 0) return;

	const headers = Object.keys(data[0]);
	const rows = data.map((row) =>
		headers.map((h) => {
			const val = row[h];
			const str = val == null ? '' : String(val);
			return str.includes(',') || str.includes('"') ? `"${str.replace(/"/g, '""')}"` : str;
		}).join(',')
	);

	const metaLine = `# Source: ${meta?.source ?? 'US Energy Data Explorer'}${meta?.unit ? ` | Unit: ${meta.unit}` : ''} | Downloaded: ${new Date().toISOString().split('T')[0]}`;
	const csv = [metaLine, headers.join(','), ...rows].join('\n');
	const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
	triggerDownload(blob, `${filename}.csv`);
}

export function downloadSVG(svgElement: SVGSVGElement, filename: string): void {
	const serializer = new XMLSerializer();
	const svgString = serializer.serializeToString(svgElement);
	const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
	triggerDownload(blob, `${filename}.svg`);
}

export async function downloadPNG(
	svgElement: SVGSVGElement,
	filename: string,
	meta?: { title?: string; source?: string }
): Promise<void> {
	const clone = svgElement.cloneNode(true) as SVGSVGElement;

	// Resolve CSS custom properties so the exported image doesn't rely on stylesheets
	const computedStyle = getComputedStyle(svgElement);
	const resolveVars = (el: SVGElement) => {
		const style = el.getAttribute('style');
		if (style) {
			el.setAttribute(
				'style',
				style.replace(/var\(--[^)]+\)/g, (match) => {
					const prop = match.slice(4, -1).trim();
					return computedStyle.getPropertyValue(prop).trim() || match;
				})
			);
		}
		for (const attr of ['fill', 'stroke', 'color']) {
			const val = el.getAttribute(attr);
			if (val?.startsWith('var(')) {
				const prop = val.slice(4, -1).trim();
				const resolved = computedStyle.getPropertyValue(prop).trim();
				if (resolved) el.setAttribute(attr, resolved);
			}
		}
		for (const child of el.children) {
			if (child instanceof SVGElement) resolveVars(child);
		}
	};
	resolveVars(clone);

	// Parse existing viewBox
	const vb = clone.getAttribute('viewBox')?.split(' ').map(Number) ?? [0, 0, 800, 400];
	const titleHeight = meta?.title ? 36 : 0;
	const sourceHeight = meta?.source ? 24 : 0;
	const newHeight = vb[3] + titleHeight + sourceHeight;

	// Wrap all existing children in a group offset down to make room for the title
	if (titleHeight > 0 || sourceHeight > 0) {
		const wrapper = document.createElementNS('http://www.w3.org/2000/svg', 'g');
		wrapper.setAttribute('transform', `translate(0, ${titleHeight})`);
		while (clone.firstChild) {
			wrapper.appendChild(clone.firstChild);
		}
		clone.appendChild(wrapper);
	}

	clone.setAttribute('viewBox', `${vb[0]} ${vb[1]} ${vb[2]} ${newHeight}`);

	// Add title text at the top
	if (meta?.title) {
		const titleEl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
		titleEl.setAttribute('x', '16');
		titleEl.setAttribute('y', '24');
		titleEl.setAttribute('font-size', '16');
		titleEl.setAttribute('font-weight', '600');
		titleEl.setAttribute('fill', computedStyle.getPropertyValue('--color-text').trim() || EXPORT_FALLBACKS.text);
		titleEl.setAttribute('font-family', 'system-ui, -apple-system, sans-serif');
		titleEl.textContent = meta.title;
		clone.insertBefore(titleEl, clone.firstChild);
	}

	// Add source attribution at the bottom
	if (meta?.source) {
		const sourceEl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
		sourceEl.setAttribute('x', '16');
		sourceEl.setAttribute('y', String(newHeight - 8));
		sourceEl.setAttribute('font-size', '11');
		sourceEl.setAttribute('fill', computedStyle.getPropertyValue('--color-text-secondary').trim() || EXPORT_FALLBACKS.textSecondary);
		sourceEl.setAttribute('font-family', 'system-ui, -apple-system, sans-serif');
		sourceEl.textContent = `Source: ${meta.source}`;
		clone.appendChild(sourceEl);
	}

	const serializer = new XMLSerializer();
	const svgString = serializer.serializeToString(clone);
	const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
	const url = URL.createObjectURL(svgBlob);

	return new Promise<void>((resolve, reject) => {
		const img = new Image();
		img.onload = () => {
			const canvas = document.createElement('canvas');
			const scale = 2; // Retina
			canvas.width = img.width * scale;
			canvas.height = img.height * scale;
			const ctx = canvas.getContext('2d')!;
			ctx.scale(scale, scale);
			ctx.fillStyle = computedStyle.getPropertyValue('--color-surface').trim() || EXPORT_FALLBACKS.surface;
			ctx.fillRect(0, 0, img.width, img.height);
			ctx.drawImage(img, 0, 0);
			URL.revokeObjectURL(url);

			canvas.toBlob((blob) => {
				if (blob) triggerDownload(blob, `${filename}.png`);
				resolve();
			}, 'image/png');
		};
		img.onerror = () => {
			URL.revokeObjectURL(url);
			console.error(`downloadPNG: failed to load SVG image for "${filename}"`);
			reject(new Error(`Failed to load SVG image for "${filename}"`));
		};
		img.src = url;
	});
}

function triggerDownload(blob: Blob, filename: string): void {
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	a.click();
	URL.revokeObjectURL(url);
}
