<script lang="ts">
	import { LOGO_GRADIENT } from '$utils/colors';

	interface Props {
		id: string;
	}

	let { id }: Props = $props();
</script>

<svg class="h-5 w-5 shrink-0 rounded-[3px]" viewBox="0 0 44 44" aria-hidden="true">
	<defs>
		<linearGradient {id} x1="0%" y1="0%" x2="100%" y2="0%">
			<stop offset="0%" stop-color={LOGO_GRADIENT[0]} />
			<stop offset="50%" stop-color={LOGO_GRADIENT[1]} />
			<stop offset="100%" stop-color={LOGO_GRADIENT[2]} />
		</linearGradient>
	</defs>
	<rect x="0" y="0" width="44" height="44" fill="#1a1a2e" />
	<path d="M 0,30.8 L 3.52,28.6 L 7.92,33 L 12.32,22 L 16.72,26.4 L 22,13.2 L 27.28,24.2 L 31.68,19.8 L 36.08,26.4 L 40.48,24.2 L 44,28.6" stroke="url(#{id})" stroke-width="1.32" fill="none" stroke-linejoin="round" />
</svg>
