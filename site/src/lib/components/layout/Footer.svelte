<script lang="ts">
	import Logo from './Logo.svelte';
</script>

<footer class="mt-16 border-t border-border bg-surface-alt">
	<div class="mx-auto flex max-w-[1100px] flex-col items-center gap-4 px-4 py-8 sm:flex-row sm:justify-between sm:gap-6">
		<!-- Brand -->
		<a href="/" class="flex items-center gap-2 font-display text-base text-text no-underline hover:text-text-secondary shrink-0">
			<Logo id="footer-logo-grad" />
			Bottlenecks Labs
		</a>

		<!-- Nav links -->
		<nav class="flex flex-wrap items-center justify-center gap-x-1 gap-y-1">
			<a href="/prices" class="text-xs text-text-muted no-underline hover:text-text-secondary transition-colors">Prices</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/demand" class="text-xs text-text-muted no-underline hover:text-text-secondary transition-colors">Demand</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/generation" class="text-xs text-text-muted no-underline hover:text-text-secondary transition-colors">Generation</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/fuels" class="text-xs text-text-muted no-underline hover:text-text-secondary transition-colors">Fuels</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/reliability" class="text-xs text-text-muted no-underline hover:text-text-secondary transition-colors">Reliability</a>
		</nav>

		<!-- Attribution -->
		<div class="flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 text-xs text-text-muted shrink-0">
			<a
				href="https://www.eia.gov/"
				target="_blank"
				rel="noopener noreferrer"
				class="text-text-muted no-underline hover:text-text-secondary transition-colors"
			>Data from the EIA &#8599;</a>
			<span class="text-text-muted/30" aria-hidden="true">&middot;</span>
			<a
				href="https://github.com/us-energy-data"
				target="_blank"
				rel="noopener noreferrer"
				class="text-text-muted no-underline hover:text-text-secondary transition-colors"
			>GitHub &#8599;</a>
			<span class="text-text-muted/30" aria-hidden="true">&middot;</span>
			<span>Updated weekly</span>
		</div>
	</div>
</footer>
