<footer class="mt-8 border-t border-border relative bg-surface-card">
	<!-- Gradient top border -->
	<div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent"></div>

	<div class="mx-auto flex max-w-5xl flex-col items-center gap-4 px-4 py-4 sm:flex-row sm:justify-between sm:gap-6">
		<!-- Brand -->
		<a href="/" class="flex items-center gap-2 font-display text-base text-text no-underline hover:text-accent shrink-0">
			<svg class="h-5 w-5 shrink-0" viewBox="0 0 44 44" aria-hidden="true">
				<rect width="44" height="44" fill="#1a1a2e" />
				<defs>
					<linearGradient id="footer-logo-grad" x1="0%" y1="0%" x2="100%" y2="0%">
						<stop offset="0%" stop-color="#2a9d8f" />
						<stop offset="50%" stop-color="#e9c46a" />
						<stop offset="100%" stop-color="#e76f51" />
					</linearGradient>
				</defs>
				<path d="M 0,30.8 L 3.52,28.6 L 7.92,33 L 12.32,22 L 16.72,26.4 L 22,13.2 L 27.28,24.2 L 31.68,19.8 L 36.08,26.4 L 40.48,24.2 L 44,28.6" stroke="url(#footer-logo-grad)" stroke-width="1.32" fill="none" stroke-linejoin="round" />
			</svg>
			Bottlenecks Labs
		</a>

		<!-- Nav links -->
		<nav class="flex flex-wrap items-center justify-center gap-x-1 gap-y-1">
			<a href="/prices" class="text-xs text-text-muted no-underline hover:text-accent transition-colors">Prices</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/demand" class="text-xs text-text-muted no-underline hover:text-accent transition-colors">Demand</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/generation" class="text-xs text-text-muted no-underline hover:text-accent transition-colors">Generation</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/fuels" class="text-xs text-text-muted no-underline hover:text-accent transition-colors">Fuels</a>
			<span class="text-text-muted/30 text-xs" aria-hidden="true">&middot;</span>
			<a href="/reliability" class="text-xs text-text-muted no-underline hover:text-accent transition-colors">Reliability</a>
		</nav>

		<!-- Attribution -->
		<div class="flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 text-xs text-text-muted shrink-0">
			<a
				href="https://www.eia.gov/"
				target="_blank"
				rel="noopener noreferrer"
				class="text-text-muted no-underline hover:text-accent transition-colors"
			>Data from the EIA &#8599;</a>
			<span class="text-text-muted/30" aria-hidden="true">&middot;</span>
			<a
				href="https://github.com/us-energy-data"
				target="_blank"
				rel="noopener noreferrer"
				class="text-text-muted no-underline hover:text-accent transition-colors"
			>GitHub &#8599;</a>
			<span class="text-text-muted/30" aria-hidden="true">&middot;</span>
			<span>Updated weekly</span>
		</div>
	</div>
</footer>
