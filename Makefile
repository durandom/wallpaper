.PHONY: install search

# Default search term for wallpapers
SEARCH_TERM ?= wallpaper rally racing

install:
	pipenv install

# Usage: make search SEARCH_TERM="nature wallpaper"
search:
	@if [ -z "$(SEARCH_TERM)" ]; then \
		echo "Please provide a search term. Usage: make search SEARCH_TERM=\"your search term\"" \
		exit 1; \
	fi
	pipenv run python image_scraper.py --max-results 100 $(SEARCH_TERM)
.PHONY: install search
