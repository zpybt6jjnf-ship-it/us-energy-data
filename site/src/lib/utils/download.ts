export function downloadCSV(data: Record<string, unknown>[], filename: string): void {
	if (data.length === 0) return;

	const headers = Object.keys(data[0]);
	const rows = data.map((row) =>
		headers.map((h) => {
			const val = row[h];
			const str = val == null ? '' : String(val);
			return str.includes(',') || str.includes('"') ? `"${str.replace(/"/g, '""')}"` : str;
		}).join(',')
	);

	const csv = [headers.join(','), ...rows].join('\n');
	const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
	triggerDownload(blob, `${filename}.csv`);
}

export function downloadSVG(svgElement: SVGSVGElement, filename: string): void {
	const serializer = new XMLSerializer();
	const svgString = serializer.serializeToString(svgElement);
	const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
	triggerDownload(blob, `${filename}.svg`);
}

export async function downloadPNG(svgElement: SVGSVGElement, filename: string): Promise<void> {
	const serializer = new XMLSerializer();
	const svgString = serializer.serializeToString(svgElement);
	const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
	const url = URL.createObjectURL(svgBlob);

	const img = new Image();
	img.onload = () => {
		const canvas = document.createElement('canvas');
		const scale = 2; // Retina
		canvas.width = img.width * scale;
		canvas.height = img.height * scale;
		const ctx = canvas.getContext('2d')!;
		ctx.scale(scale, scale);
		ctx.fillStyle = '#ffffff';
		ctx.fillRect(0, 0, img.width, img.height);
		ctx.drawImage(img, 0, 0);
		URL.revokeObjectURL(url);

		canvas.toBlob((blob) => {
			if (blob) triggerDownload(blob, `${filename}.png`);
		}, 'image/png');
	};
	img.src = url;
}

function triggerDownload(blob: Blob, filename: string): void {
	const url = URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = filename;
	a.click();
	URL.revokeObjectURL(url);
}
