SHELL=/bin/bash

.PHONY: local deploy clean

local:
	tools/local_server.sh

deploy:
	@if [ `whoami` = 'vim' ]; then \
		tools/deploy.sh; \
	else \
		cat tools/deploy.sh | ssh vim@vim.benalpert.com sh; \
	fi

seed_data:
	@echo "Creating tables with some example data"
	python db/seed.py
	@echo
	@echo "Scraping some repos from the vim-scripts GitHub org"
	python tools/scrape/scrape.py 40

clean:
	find . -name '*.pyc' -delete
	bundle exec compass clean --config conf/compass.rb
