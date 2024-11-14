.PHONY: install search

# Default minimum resolution
RESOLUTION ?= 1920x1080

install:
	pipenv install

# Usage: make search TERM="cats" [RESOLUTION="1920x1080"]
search:
	@if [ -z "$(TERM)" ]; then \
		echo "Please provide a search term. Usage: make search TERM=\"your search term\" [RESOLUTION=\"widthxheight\"]"; \
		exit 1; \
	fi
	pipenv run python image_scraper.py "$(TERM)" --resolution "$(RESOLUTION)"
.PHONY: install search